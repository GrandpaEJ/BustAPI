//! Python route handlers

use pyo3::prelude::*;

use crate::bindings::converters::*;
use crate::bindings::request::create_py_request;
use crate::request::RequestData;
use crate::response::ResponseData;
use crate::router::RouteHandler;

/// Python route handler - calls Python function for each request
/// With Python 3.13 free-threaded mode, no GIL bottleneck!
pub struct PyRouteHandler {
    handler: PyObject,
}

impl PyRouteHandler {
    pub fn new(handler: PyObject) -> Self {
        Self { handler }
    }
}

impl RouteHandler for PyRouteHandler {
    fn handle(&self, req: RequestData) -> ResponseData {
        // With Python 3.13t, this runs in parallel without GIL blocking!
        Python::with_gil(|py| {
            // Create request data
            let py_req = create_py_request(py, &req);

            match py_req {
                Ok(py_req_obj) => {
                    // Call Python handler
                    match self.handler.call1(py, (py_req_obj,)) {
                        Ok(result) => convert_py_result_to_response(py, result),
                        Err(e) => {
                            tracing::error!("Python handler error: {:?}", e);
                            ResponseData::error(
                                actix_web::http::StatusCode::INTERNAL_SERVER_ERROR,
                                Some("Handler error"),
                            )
                        }
                    }
                }
                Err(e) => {
                    tracing::error!("Request creation error: {:?}", e);
                    ResponseData::error(
                        actix_web::http::StatusCode::INTERNAL_SERVER_ERROR,
                        Some("Request error"),
                    )
                }
            }
        })
    }
}

/// Async Python route handler
pub struct PyAsyncRouteHandler {
    handler: PyObject,
}

impl PyAsyncRouteHandler {
    pub fn new(handler: PyObject) -> Self {
        Self { handler }
    }
}

impl RouteHandler for PyAsyncRouteHandler {
    fn handle(&self, req: RequestData) -> ResponseData {
        // For async handlers, call and check if coroutine
        Python::with_gil(|py| {
            let py_req = create_py_request(py, &req);

            match py_req {
                Ok(py_req_obj) => {
                    match self.handler.call1(py, (py_req_obj,)) {
                        Ok(result) => {
                            // Check if coroutine
                            let asyncio = py.import("asyncio");
                            if let Ok(asyncio) = asyncio {
                                match asyncio.call_method1("iscoroutine", (&result,)) {
                                    Ok(is_coro) => {
                                        let is_coro_bool =
                                            is_coro.extract::<bool>().unwrap_or(false);
                                        tracing::debug!(
                                            "Async handler result type: {}, is_coro: {}",
                                            result
                                                .bind(py)
                                                .get_type()
                                                .name()
                                                .ok()
                                                .map(|s| s.to_string())
                                                .unwrap_or("unknown".to_string()),
                                            is_coro_bool
                                        );

                                        if is_coro_bool {
                                            // Run coroutine
                                            if let Ok(_loop_obj) =
                                                asyncio.call_method0("NewEventLoop")
                                            { // Try new loop? No get_event_loop
                                                 // ...
                                            }
                                            // Revert to old logic but with logging
                                            if let Ok(loop_obj) =
                                                asyncio.call_method0("get_event_loop")
                                            {
                                                if let Ok(awaited) = loop_obj
                                                    .call_method1("run_until_complete", (&result,))
                                                {
                                                    return convert_py_result_to_response(
                                                        py,
                                                        awaited.into(),
                                                    );
                                                } else {
                                                    tracing::error!("run_until_complete failed");
                                                }
                                            } else {
                                                // Try new loop if get_event_loop fails (e.g. no loop in thread)
                                                if let Ok(loop_obj) =
                                                    asyncio.call_method0("new_event_loop")
                                                {
                                                    let _ = asyncio.call_method1(
                                                        "set_event_loop",
                                                        (&loop_obj,),
                                                    );
                                                    if let Ok(awaited) = loop_obj.call_method1(
                                                        "run_until_complete",
                                                        (&result,),
                                                    ) {
                                                        return convert_py_result_to_response(
                                                            py,
                                                            awaited.into(),
                                                        );
                                                    }
                                                }
                                                tracing::error!("Failed to get/create event loop");
                                            }
                                        }
                                    }
                                    Err(e) => tracing::error!("iscoroutine check failed: {:?}", e),
                                }
                            }
                            convert_py_result_to_response(py, result)
                        }
                        Err(e) => {
                            tracing::error!("Async handler error: {:?}", e);
                            ResponseData::error(
                                actix_web::http::StatusCode::INTERNAL_SERVER_ERROR,
                                Some("Async handler error"),
                            )
                        }
                    }
                }
                Err(e) => {
                    tracing::error!("Request creation error: {:?}", e);
                    ResponseData::error(
                        actix_web::http::StatusCode::INTERNAL_SERVER_ERROR,
                        Some("Request error"),
                    )
                }
            }
        })
    }
}
