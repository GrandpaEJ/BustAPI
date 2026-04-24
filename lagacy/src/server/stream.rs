use actix_web::{web::Bytes, Error};
use futures::Stream;
use pyo3::exceptions::{PyRuntimeError, PyStopAsyncIteration, PyStopIteration, PyTypeError};
use pyo3::prelude::*;
use std::future::Future;
use std::pin::Pin;
use std::task::{Context, Poll};

enum StreamMode {
    Sync,
    Async,
}

type StreamFuture = Pin<Box<dyn Future<Output = Option<Result<Vec<u8>, PyErr>>> + Send>>;

pub struct PythonStream {
    iterator: Py<PyAny>,
    mode: StreamMode,
    fut: Option<StreamFuture>,
}

// Safety: Py<PyAny> is generally Send if we hold the GIL when accessing it,
// and we are using spawn_blocking or into_future which handles thread safety.
unsafe impl Send for PythonStream {}

impl PythonStream {
    pub fn new(iterator: Py<PyAny>) -> Self {
        let mode = Python::attach(|py| {
            // Check for __anext__ to detect async iterator
            if iterator.bind(py).hasattr("__anext__").unwrap_or(false) {
                StreamMode::Async
            } else {
                StreamMode::Sync
            }
        });

        Self {
            iterator,
            mode,
            fut: None,
        }
    }
}

impl Stream for PythonStream {
    type Item = Result<Bytes, Error>;

    fn poll_next(mut self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<Option<Self::Item>> {
        if self.fut.is_none() {
            let iterator = Python::attach(|py| self.iterator.clone_ref(py));

            let fut = match self.mode {
                StreamMode::Sync => {
                    // Sync Iterator: Run in blocking task
                    Box::pin(async move {
                        let res = tokio::task::spawn_blocking(move || {
                            Python::attach(|py| {
                                let iter_bound = iterator.bind(py);
                                // Call __next__ directly
                                match iter_bound.call_method0("__next__") {
                                    Ok(item) => process_item(py, item),
                                    Err(e) => {
                                        if e.is_instance_of::<PyStopIteration>(py) {
                                            None
                                        } else {
                                            Some(Err(e))
                                        }
                                    }
                                }
                            })
                        })
                        .await;

                        match res {
                            Ok(ok) => ok,
                            Err(_) => Some(Err(PyErr::new::<PyRuntimeError, _>("Task Join Error"))),
                        }
                    }) as StreamFuture
                }

                StreamMode::Async => {
                    // Async Iterator: Use pyo3-async-runtimes
                    Box::pin(async move {
                        // We need to call __anext__ and await the returned coroutine
                        // This requires holding GIL to call __anext__, then converting awaitable to Rust Future

                        let future_result = Python::attach(|py| {
                            let iter_bound = iterator.bind(py);
                            match iter_bound.call_method0("__anext__") {
                                Ok(awaitable) => {
                                    // Convert python awaitable to rust future
                                    // We use pyo3_async_runtimes::tokio::into_future
                                    match pyo3_async_runtimes::tokio::into_future(awaitable) {
                                        Ok(f) => Ok(f),
                                        Err(e) => Err(e),
                                    }
                                }
                                Err(e) => Err(e),
                            }
                        });

                        match future_result {
                            Ok(f) => {
                                // Await the future
                                match f.await {
                                    Ok(item) => {
                                        // Process the item (must re-acquire GIL to inspect item?)
                                        // item is PyObject (or whatever into_future returns? default is PyObject)
                                        let item_obj: Py<PyAny> = item;
                                        Python::attach(|py| {
                                            process_item(py, item_obj.into_bound(py))
                                        })
                                    }
                                    Err(e) => Python::attach(|py| {
                                        if e.is_instance_of::<PyStopAsyncIteration>(py) {
                                            None
                                        } else {
                                            Some(Err(e))
                                        }
                                    }),
                                }
                            }
                            Err(e) => Python::attach(|py| {
                                if e.is_instance_of::<PyStopAsyncIteration>(py) {
                                    None
                                } else {
                                    Some(Err(e))
                                }
                            }),
                        }
                    })
                }
            };

            self.fut = Some(fut);
        }

        // Poll the future
        if let Some(fut) = self.fut.as_mut() {
            match fut.as_mut().poll(cx) {
                Poll::Ready(result) => {
                    self.fut = None; // Reset for next iteration
                    match result {
                        None => Poll::Ready(None),
                        Some(Ok(bytes)) => Poll::Ready(Some(Ok(Bytes::from(bytes)))),
                        Some(Err(e)) => Poll::Ready(Some(Err(
                            actix_web::error::ErrorInternalServerError(e.to_string()),
                        ))),
                    }
                }
                Poll::Pending => Poll::Pending,
            }
        } else {
            Poll::Pending
        }
    }
}

// Helper to extract bytes/string from item
fn process_item(_py: Python, item: Bound<'_, PyAny>) -> Option<Result<Vec<u8>, PyErr>> {
    if let Ok(bytes) = item.extract::<Vec<u8>>() {
        Some(Ok(bytes))
    } else if let Ok(s) = item.extract::<String>() {
        Some(Ok(s.into_bytes()))
    } else {
        // Try encoding
        match item.call_method0("encode") {
            Ok(enc) => {
                if let Ok(bytes) = enc.extract::<Vec<u8>>() {
                    Some(Ok(bytes))
                } else {
                    Some(Err(PyErr::new::<PyTypeError, _>(
                        "Stream yielded non-bytes",
                    )))
                }
            }
            Err(e) => Some(Err(e)),
        }
    }
}
