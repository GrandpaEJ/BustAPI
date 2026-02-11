use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList, PyString};
use std::collections::HashMap;

use crate::request::RequestData;
use crate::response::ResponseData;
use crate::router::RouteHandler;
use super::typed_turbo::{ParamType, TypedValue};

#[derive(Clone, Debug)]
pub enum Op {
    Add,
    Sub,
    Mul,
    Div,
}

/// Represents a node in the expression tree (AST)
#[derive(Clone, Debug)]
pub enum ExprNode {
    Value(TraceValue),
    LiteralInt(i64),
    LiteralFloat(f64),
    BinaryOp(Box<ExprNode>, Op, Box<ExprNode>),
}

/// Python wrapper for an expression
#[pyclass]
#[derive(Clone, Debug)]
pub struct TraceExpr {
    pub node: ExprNode,
}

#[pymethods]
impl TraceExpr {
    fn __add__(&self, other: &Bound<PyAny>) -> PyResult<Self> {
        let right = Self::extract_node(other)?;
        Ok(TraceExpr {
            node: ExprNode::BinaryOp(Box::new(self.node.clone()), Op::Add, Box::new(right)),
        })
    }
    
    fn __sub__(&self, other: &Bound<PyAny>) -> PyResult<Self> {
        let right = Self::extract_node(other)?;
        Ok(TraceExpr {
            node: ExprNode::BinaryOp(Box::new(self.node.clone()), Op::Sub, Box::new(right)),
        })
    }

    fn __mul__(&self, other: &Bound<PyAny>) -> PyResult<Self> {
        let right = Self::extract_node(other)?;
        Ok(TraceExpr {
            node: ExprNode::BinaryOp(Box::new(self.node.clone()), Op::Mul, Box::new(right)),
        })
    }
    
    fn __truediv__(&self, other: &Bound<PyAny>) -> PyResult<Self> {
        let right = Self::extract_node(other)?;
        Ok(TraceExpr {
            node: ExprNode::BinaryOp(Box::new(self.node.clone()), Op::Div, Box::new(right)),
        })
    }
}

impl TraceExpr {
    fn extract_node(obj: &Bound<PyAny>) -> PyResult<ExprNode> {
        if let Ok(expr) = obj.extract::<TraceExpr>() {
            Ok(expr.node)
        } else if let Ok(trace) = obj.extract::<TraceValue>() {
            Ok(ExprNode::Value(trace))
        } else if let Ok(i) = obj.extract::<i64>() {
            Ok(ExprNode::LiteralInt(i))
        } else if let Ok(f) = obj.extract::<f64>() {
            Ok(ExprNode::LiteralFloat(f))
        } else {
            Err(pyo3::exceptions::PyTypeError::new_err("Invalid operand type"))
        }
    }
}

/// Trace object used during route compilation
#[pyclass]
#[derive(Clone, Debug)]
pub struct TraceValue {
    #[pyo3(get)]
    pub name: String,
    #[pyo3(get)]
    pub type_name: String,
}

#[pymethods]
impl TraceValue {
    #[new]
    fn new(name: String, type_name: String) -> Self {
        Self { name, type_name }
    }
    
    fn __repr__(&self) -> String {
        format!("<TraceValue {}:{}>", self.name, self.type_name)
    }

    // Operator overloading for TraceValue (promotes to TraceExpr)
    fn __add__(&self, other: &Bound<PyAny>) -> PyResult<TraceExpr> {
        let left = ExprNode::Value(self.clone());
        let right = TraceExpr::extract_node(other)?;
        Ok(TraceExpr { node: ExprNode::BinaryOp(Box::new(left), Op::Add, Box::new(right)) })
    }
    
    fn __sub__(&self, other: &Bound<PyAny>) -> PyResult<TraceExpr> {
        let left = ExprNode::Value(self.clone());
        let right = TraceExpr::extract_node(other)?;
        Ok(TraceExpr { node: ExprNode::BinaryOp(Box::new(left), Op::Sub, Box::new(right)) })
    }
    
    fn __mul__(&self, other: &Bound<PyAny>) -> PyResult<TraceExpr> {
        let left = ExprNode::Value(self.clone());
        let right = TraceExpr::extract_node(other)?;
        Ok(TraceExpr { node: ExprNode::BinaryOp(Box::new(left), Op::Mul, Box::new(right)) })
    }
    
    fn __truediv__(&self, other: &Bound<PyAny>) -> PyResult<TraceExpr> {
        let left = ExprNode::Value(self.clone());
        let right = TraceExpr::extract_node(other)?;
        Ok(TraceExpr { node: ExprNode::BinaryOp(Box::new(left), Op::Div, Box::new(right)) })
    }
}

/// A part of the compiled response template
#[derive(Debug, Clone)]
enum TemplatePart {
    Static(Vec<u8>),       // "{\"id\": "
    Dynamic(String),       // "id" (param name)
    Expression(ExprNode),  // Abstract Syntax Tree
}

/// Handler that executes a pre-compiled response template
#[pyclass]
pub struct PyCompiledHandler {
    pattern_parts: Vec<String>,
    param_specs: Vec<(String, ParamType)>,
    template: Vec<TemplatePart>,
}

#[pymethods]
impl PyCompiledHandler {
    #[new]
    pub fn new(
        py: Python,
        structure: Py<PyAny>, // The result of calling the handler with Traces (e.g. {"a": TraceValue("a")})
        pattern: String,
        param_types: HashMap<String, String>,
    ) -> PyResult<Self> {
        let pattern_parts: Vec<String> = pattern
            .trim_matches('/')
            .split('/')
            .map(|s| s.to_string())
            .collect();
            
        let mut specs = Vec::new();
        for part in pattern.split('/') {
            if part.starts_with('<') && part.ends_with('>') {
                let inner = &part[1..part.len() - 1];
                let name = if let Some((_, n)) = inner.split_once(':') {
                    n.trim().to_string()
                } else {
                    inner.trim().to_string()
                };
                let param_type = param_types
                    .get(&name)
                    .map(|t| ParamType::from_str(t))
                    .unwrap_or(ParamType::Str);
                specs.push((name, param_type));
            }
        }

        // Compile the structure into a template
        let mut template = Vec::new();
        Self::compile_structure(py, structure.bind(py), &mut template)?;

        Ok(Self {
            pattern_parts,
            param_specs: specs,
            template,
        })
    }
}

impl PyCompiledHandler {
    fn compile_structure(py: Python, obj: &Bound<'_, PyAny>, template: &mut Vec<TemplatePart>) -> PyResult<()> {
        if let Ok(expr) = obj.extract::<TraceExpr>() {
            template.push(TemplatePart::Expression(expr.node));
        } else if let Ok(trace) = obj.extract::<TraceValue>() {
            // It's a TraceValue, emit a Dynamic part
            template.push(TemplatePart::Dynamic(trace.name));
        } else if let Ok(dict) = obj.downcast::<PyDict>() {
            template.push(TemplatePart::Static(b"{".to_vec()));
            let mut first = true;
            for (key, value) in dict {
                if !first {
                    template.push(TemplatePart::Static(b",".to_vec()));
                }
                first = false;
                
                // Key (assume string)
                let key_str = key.to_string();
                template.push(TemplatePart::Static(format!("\"{}\":", key_str).into_bytes()));
                
                // Value (recurse)
                Self::compile_structure(py, &value, template)?;
            }
            template.push(TemplatePart::Static(b"}".to_vec()));
        } else if let Ok(list) = obj.downcast::<PyList>() {
            template.push(TemplatePart::Static(b"[".to_vec()));
            let mut first = true;
            for item in list {
                if !first {
                    template.push(TemplatePart::Static(b",".to_vec()));
                }
                first = false;
                Self::compile_structure(py, &item, template)?;
            }
            template.push(TemplatePart::Static(b"]".to_vec()));
        } else if let Ok(s) = obj.downcast::<PyString>() {
            // Static string
            let s_val = s.to_str()?;
            template.push(TemplatePart::Static(format!("\"{}\"", s_val).into_bytes()));
        } else if let Ok(i) = obj.extract::<i64>() {
             // Static int
             template.push(TemplatePart::Static(i.to_string().into_bytes()));
        } else if let Ok(f) = obj.extract::<f64>() {
             // Static float
             template.push(TemplatePart::Static(f.to_string().into_bytes()));
        } else if obj.is_none() {
             template.push(TemplatePart::Static(b"null".to_vec()));
        } else if let Ok(b) = obj.extract::<bool>() {
             template.push(TemplatePart::Static(if b { b"true".to_vec() } else { b"false".to_vec() }));
        } else {
             // Fallback for unknown types (try string repr)
             let s_bound = obj.str()?;
             let s = s_bound.to_str()?;
             template.push(TemplatePart::Static(format!("\"{}\"", s).into_bytes()));
        }
        Ok(())
    }
    
    // Copy-paste extract_params from TypedTurbo (ideally should be shared trait/mixin)
    fn extract_params(&self, path: &str) -> Result<HashMap<String, TypedValue>, String> {
        if self.param_specs.is_empty() {
             return Ok(HashMap::new());
        }

        let mut params = HashMap::new();
        let mut spec_idx = 0;
        let mut path_segments = path.trim_matches('/').split('/');

        for pp in &self.pattern_parts {
            if pp.starts_with('<') && pp.ends_with('>') {
                if spec_idx >= self.param_specs.len() {
                    return Err("Parameter spec mismatch".to_string());
                }

                let (name, param_type) = &self.param_specs[spec_idx];
                spec_idx += 1;

                if matches!(param_type, ParamType::Path) {
                    let remaining: Vec<&str> = path_segments.collect();
                    let remaining_str = remaining.join("/");
                    params.insert(name.clone(), TypedValue::Str(remaining_str));
                    break;
                }

                let value = match path_segments.next() {
                    Some(v) => v,
                    None => return Err(format!("Missing path segment for parameter '{}'", name)),
                };
                
                let typed_value = match param_type {
                    ParamType::Int => {
                        match value.parse::<i64>() {
                            Ok(n) => TypedValue::Int(n),
                            Err(_) => {
                                if value.chars().all(|c| c.is_ascii_digit() || c == '-') {
                                    TypedValue::BigInt(value.to_string())
                                } else {
                                    return Err(format!("Invalid int for '{}'", name));
                                }
                            }
                        }
                    }
                    ParamType::Float => match value.parse::<f64>() {
                        Ok(n) => TypedValue::Float(n),
                        Err(_) => return Err(format!("Invalid float for '{}'", name))
                    },
                    ParamType::Str | ParamType::Path => TypedValue::Str(value.to_string()),
                };

                params.insert(name.clone(), typed_value);
            } else {
                 path_segments.next();
            }
        }
        Ok(params)
    }

    fn evaluate_expr(node: &ExprNode, params: &HashMap<String, TypedValue>) -> Result<TypedValue, String> {
        match node {
            ExprNode::Value(trace) => params.get(&trace.name)
                .cloned()
                .ok_or_else(|| format!("Missing param {}", trace.name)),
            ExprNode::LiteralInt(i) => Ok(TypedValue::Int(*i)),
            ExprNode::LiteralFloat(f) => Ok(TypedValue::Float(*f)),
            ExprNode::BinaryOp(left, op, right) => {
                let l_val = Self::evaluate_expr(left, params)?;
                let r_val = Self::evaluate_expr(right, params)?;

                match (l_val, r_val) {
                    (TypedValue::Int(l), TypedValue::Int(r)) => match op {
                        Op::Add => Ok(TypedValue::Int(l + r)),
                        Op::Sub => Ok(TypedValue::Int(l - r)),
                        Op::Mul => Ok(TypedValue::Int(l * r)),
                        Op::Div => Ok(TypedValue::Float(l as f64 / r as f64)), // Py div
                    },
                    (TypedValue::Float(l), TypedValue::Float(r)) => match op {
                        Op::Add => Ok(TypedValue::Float(l + r)),
                        Op::Sub => Ok(TypedValue::Float(l - r)),
                        Op::Mul => Ok(TypedValue::Float(l * r)),
                        Op::Div => Ok(TypedValue::Float(l / r)),
                    },
                    // Mixed
                     (TypedValue::Int(l), TypedValue::Float(r)) => match op {
                        Op::Add => Ok(TypedValue::Float(l as f64 + r)),
                        Op::Sub => Ok(TypedValue::Float(l as f64 - r)),
                        Op::Mul => Ok(TypedValue::Float(l as f64 * r)),
                        Op::Div => Ok(TypedValue::Float(l as f64 / r)),
                    },
                    (TypedValue::Float(l), TypedValue::Int(r)) => match op {
                        Op::Add => Ok(TypedValue::Float(l + r as f64)),
                        Op::Sub => Ok(TypedValue::Float(l - r as f64)),
                        Op::Mul => Ok(TypedValue::Float(l * r as f64)),
                        Op::Div => Ok(TypedValue::Float(l / r as f64)),
                    },
                    _ => Err("Unsupported operand types".to_string()),
                }
            }
        }
    }
}

impl RouteHandler for PyCompiledHandler {
    fn handle(&self, req: RequestData) -> ResponseData {
         // 1. Extract Params (Pure Rust)
         let params = match self.extract_params(&req.path) {
            Ok(p) => p,
            Err(e) => return ResponseData::json_error(actix_web::http::StatusCode::BAD_REQUEST, &e),
        };
        
        // 2. Render Template (Pure Rust)
        let mut body = Vec::new();
        // pre-allocate reasonable size?
        
        for part in &self.template {
            match part {
                TemplatePart::Static(bytes) => body.extend_from_slice(bytes),
                TemplatePart::Dynamic(name) => {
                    if let Some(val) = params.get(name) {
                        Self::write_value(&mut body, val);
                    } else {
                         body.extend_from_slice(b"null");
                    }
                }
                TemplatePart::Expression(expr) => {
                    match Self::evaluate_expr(expr, &params) {
                        Ok(val) => Self::write_value(&mut body, &val),
                        Err(_) => body.extend_from_slice(b"null"), // Error handling?
                    }
                }
            }
        }
        
        let mut headers = HashMap::new();
        headers.insert("Content-Type".to_string(), "application/json".to_string());

        ResponseData {
             status: actix_web::http::StatusCode::OK,
             headers,
             body,
             file_path: None,
             stream_iterator: None,
        }
    }
}

impl PyCompiledHandler {
    fn write_value(body: &mut Vec<u8>, val: &TypedValue) {
        match val {
            TypedValue::Int(n) => body.extend_from_slice(n.to_string().as_bytes()),
            TypedValue::BigInt(s) => body.extend_from_slice(s.as_bytes()),
            TypedValue::Float(f) => body.extend_from_slice(f.to_string().as_bytes()),
            TypedValue::Str(s) => {
                // Important: Encode string values as JSON string
                body.push(b'"');
                body.extend_from_slice(s.as_bytes()); // TODO: escape JSON special chars provided by explicit feature
                body.push(b'"');
            }
        }
    }
}
