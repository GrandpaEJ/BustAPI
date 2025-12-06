//! Python route handlers

use actix_web::{web, HttpRequest, HttpResponse};
use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyDict, PyString, PyTuple};
use std::collections::HashMap;

use crate::bindings::converters::*;
use crate::bindings::request::create_py_request;

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

impl crate::server::RouteHandler for PyRouteHandler {
    fn handle(&self, req: &HttpRequest, body: web::Bytes) -> HttpResponse {
        // With Python 3.13t, this runs in parallel without GIL blocking!
        Python::with_gil(|py| {
            // Create request data
            let py_req = create_py_request(py, req, &body);

            match py_req {
                Ok(py_req_obj) => {
                    // Call Python handler
                    match self.handler.call1(py, (py_req_obj,)) {
                        Ok(result) => convert_py_result_to_response(py, result),
                        Err(e) => {
                            tracing::error!("Python handler error: {:?}", e);
                            HttpResponse::InternalServerError()
                                .content_type("application/json")
                                .body(r#"{"error": "Handler error"}"#)
                        }
                    }
                }
                Err(e) => {
                    tracing::error!("Request creation error: {:?}", e);
                    HttpResponse::InternalServerError()
                        .content_type("application/json")
                        .body(r#"{"error": "Request error"}"#)
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

impl crate::server::RouteHandler for PyAsyncRouteHandler {
    fn handle(&self, req: &HttpRequest, body: web::Bytes) -> HttpResponse {
        // For async handlers, call and check if coroutine
        Python::with_gil(|py| {
            let py_req = create_py_request(py, req, &body);

            match py_req {
                Ok(py_req_obj) => {
                    match self.handler.call1(py, (py_req_obj,)) {
                        Ok(result) => {
                            // Check if coroutine
                            let asyncio = py.import("asyncio");
                            if let Ok(asyncio) = asyncio {
                                if let Ok(is_coro) = asyncio.call_method1("iscoroutine", (&result,))
                                {
                                    if is_coro.extract::<bool>().unwrap_or(false) {
                                        // Run coroutine
                                        if let Ok(loop_obj) = asyncio.call_method0("get_event_loop")
                                        {
                                            if let Ok(awaited) = loop_obj
                                                .call_method1("run_until_complete", (&result,))
                                            {
                                                return convert_py_result_to_response(
                                                    py,
                                                    awaited.into(),
                                                );
                                            }
                                        }
                                    }
                                }
                            }
                            convert_py_result_to_response(py, result)
                        }
                        Err(e) => {
                            tracing::error!("Async handler error: {:?}", e);
                            HttpResponse::InternalServerError()
                                .content_type("application/json")
                                .body(r#"{"error": "Async handler error"}"#)
                        }
                    }
                }
                Err(e) => {
                    tracing::error!("Request creation error: {:?}", e);
                    HttpResponse::InternalServerError()
                        .content_type("application/json")
                        .body(r#"{"error": "Request error"}"#)
                }
            }
        })
    }
}
