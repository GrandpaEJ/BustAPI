use argon2::{
    password_hash::{rand_core::OsRng, PasswordHash, PasswordHasher, PasswordVerifier, SaltString},
    Argon2,
};
use base64::Engine;
use cookie::{Cookie, CookieJar, Key};
use pyo3::prelude::*;
use rand::{thread_rng, Rng};
use sha2::{Digest, Sha512};

#[pyclass]
pub struct Signer {
    key: Key,
}

#[pymethods]
impl Signer {
    #[new]
    pub fn new(secret_key: &str) -> PyResult<Self> {
        if secret_key.is_empty() {
            return Err(pyo3::exceptions::PyValueError::new_err(
                "Secret key cannot be empty.",
            ));
        }

        // Use SHA512 to hash the input key to exactly 64 bytes
        // cookie::Key::from requires 64 bytes for signing+encryption master key.
        let mut hasher = Sha512::new();
        hasher.update(secret_key.as_bytes());
        let result = hasher.finalize();

        // result is GenericArray<u8, 64>
        let key = Key::from(&result);
        Ok(Signer { key })
    }

    /// Signs a value directly, returning the signed string suitable for a cookie value.
    pub fn sign(&self, name: &str, value: &str) -> PyResult<String> {
        let mut jar = CookieJar::new();
        // Cookie lib needs owned strings if they don't live long enough
        let c = Cookie::build((name.to_string(), value.to_string())).build();
        jar.signed_mut(&self.key).add(c);

        if let Some(cookie) = jar.get(name) {
            Ok(cookie.value().to_string())
        } else {
            Err(pyo3::exceptions::PyValueError::new_err(
                "Failed to sign cookie",
            ))
        }
    }

    pub fn verify(&self, name: &str, signed_value: &str) -> PyResult<Option<String>> {
        let mut jar = CookieJar::new();
        // Use owned strings
        let c = Cookie::build((name.to_string(), signed_value.to_string())).build();
        jar.add_original(c);

        if let Some(cookie) = jar.signed(&self.key).get(name) {
            return Ok(Some(cookie.value().to_string()));
        }
        Ok(None)
    }

    /// Encode a session dict to a signed cookie value (JSON → Base64 → Sign)
    /// This performs all serialization in Rust for maximum performance.
    /// 
    /// Args:
    ///     name: Cookie name (used in signature)
    ///     data: Python dict to serialize
    /// 
    /// Returns:
    ///     Signed cookie value string
    pub fn encode_session(&self, name: &str, data: &Bound<'_, pyo3::types::PyDict>) -> PyResult<String> {
        // 1. Convert PyDict to serde_json::Value
        let json_value = pythondict_to_json(data)?;
        
        // 2. Serialize to JSON string
        let json_str = serde_json::to_string(&json_value)
            .map_err(|e| pyo3::exceptions::PyValueError::new_err(format!("JSON serialization error: {}", e)))?;
        
        // 3. Base64 encode
        let b64_payload = base64::engine::general_purpose::URL_SAFE.encode(json_str.as_bytes());
        
        // 4. Sign using cookie crate
        self.sign(name, &b64_payload)
    }

    /// Decode a signed cookie value to a Python dict (Verify → Base64 → JSON)
    /// This performs all deserialization in Rust for maximum performance.
    /// 
    /// Args:
    ///     name: Cookie name (used in signature verification)
    ///     signed_value: The signed cookie value
    /// 
    /// Returns:
    ///     Python dict if valid, None if signature invalid or decode error
    pub fn decode_session<'py>(&self, py: Python<'py>, name: &str, signed_value: &str) -> PyResult<Option<Bound<'py, pyo3::types::PyDict>>> {
        // 1. Verify signature
        let payload = match self.verify(name, signed_value)? {
            Some(p) => p,
            None => return Ok(None),
        };

        // 2. Base64 decode
        let json_bytes = match base64::engine::general_purpose::URL_SAFE.decode(&payload) {
            Ok(b) => b,
            Err(_) => return Ok(None),
        };

        // 3. Parse JSON
        let json_str = match String::from_utf8(json_bytes) {
            Ok(s) => s,
            Err(_) => return Ok(None),
        };

        let json_value: serde_json::Value = match serde_json::from_str(&json_str) {
            Ok(v) => v,
            Err(_) => return Ok(None),
        };

        // 4. Convert to PyDict
        json_to_pydict(py, &json_value)
    }
}

/// Convert a Python dict to serde_json::Value
fn pythondict_to_json(dict: &Bound<'_, pyo3::types::PyDict>) -> PyResult<serde_json::Value> {
    use pyo3::types::{PyBool, PyFloat, PyInt, PyList, PyString};
    use serde_json::{Map, Value};

    let mut map = Map::new();
    for (key, value) in dict.iter() {
        let key_str: String = key.extract()?;
        let json_val = python_to_json_value(&value)?;
        map.insert(key_str, json_val);
    }
    Ok(Value::Object(map))
}

/// Convert a Python object to serde_json::Value
fn python_to_json_value(obj: &Bound<'_, pyo3::types::PyAny>) -> PyResult<serde_json::Value> {
    use pyo3::types::{PyBool, PyDict, PyFloat, PyInt, PyList, PyNone, PyString};
    use serde_json::Value;

    if obj.is_none() || obj.is_instance_of::<PyNone>() {
        Ok(Value::Null)
    } else if let Ok(b) = obj.downcast::<PyBool>() {
        Ok(Value::Bool(b.is_true()))
    } else if let Ok(i) = obj.downcast::<PyInt>() {
        let val: i64 = i.extract()?;
        Ok(Value::Number(val.into()))
    } else if let Ok(f) = obj.downcast::<PyFloat>() {
        let val: f64 = f.extract()?;
        Ok(serde_json::Number::from_f64(val)
            .map(Value::Number)
            .unwrap_or(Value::Null))
    } else if let Ok(s) = obj.downcast::<PyString>() {
        let val: String = s.extract()?;
        Ok(Value::String(val))
    } else if let Ok(list) = obj.downcast::<PyList>() {
        let arr: Result<Vec<Value>, _> = list.iter().map(|item| python_to_json_value(&item)).collect();
        Ok(Value::Array(arr?))
    } else if let Ok(dict) = obj.downcast::<PyDict>() {
        pythondict_to_json(dict)
    } else {
        // Fallback: try to convert to string
        let s: String = obj.str()?.extract()?;
        Ok(Value::String(s))
    }
}

/// Convert serde_json::Value to Python dict
fn json_to_pydict<'py>(py: Python<'py>, value: &serde_json::Value) -> PyResult<Option<Bound<'py, pyo3::types::PyDict>>> {
    use serde_json::Value;

    match value {
        Value::Object(map) => {
            let dict = pyo3::types::PyDict::new(py);
            for (k, v) in map {
                let py_val = json_to_pyobject(py, v)?;
                dict.set_item(k, py_val)?;
            }
            Ok(Some(dict))
        }
        _ => Ok(None),
    }
}

/// Convert serde_json::Value to PyObject
fn json_to_pyobject(py: Python<'_>, value: &serde_json::Value) -> PyResult<pyo3::Py<pyo3::types::PyAny>> {
    use pyo3::IntoPyObjectExt;
    use serde_json::Value;

    match value {
        Value::Null => Ok(py.None()),
        Value::Bool(b) => Ok(b.into_py_any(py)?),
        Value::Number(n) => {
            if let Some(i) = n.as_i64() {
                Ok(i.into_py_any(py)?)
            } else if let Some(f) = n.as_f64() {
                Ok(f.into_py_any(py)?)
            } else {
                Ok(py.None())
            }
        }
        Value::String(s) => Ok(s.clone().into_py_any(py)?),
        Value::Array(arr) => {
            let list = pyo3::types::PyList::empty(py);
            for item in arr {
                list.append(json_to_pyobject(py, item)?)?;
            }
            Ok(list.into_any().unbind())
        }
        Value::Object(map) => {
            let dict = pyo3::types::PyDict::new(py);
            for (k, v) in map {
                dict.set_item(k, json_to_pyobject(py, v)?)?;
            }
            Ok(dict.into_any().unbind())
        }
    }
}

// ============================================================================
// Password Hashing with Argon2id
// ============================================================================

/// Hash a password using Argon2id (recommended by OWASP)
///
/// Args:
///     password: Plain text password to hash
///
/// Returns:
///     PHC-formatted hash string (includes salt and parameters)
#[pyfunction]
pub fn hash_password(password: &str) -> PyResult<String> {
    let salt = SaltString::generate(&mut OsRng);
    let argon2 = Argon2::default();

    argon2
        .hash_password(password.as_bytes(), &salt)
        .map(|hash| hash.to_string())
        .map_err(|e| pyo3::exceptions::PyValueError::new_err(format!("Hashing error: {}", e)))
}

/// Verify a password against a hash
///
/// Args:
///     password: Plain text password to verify
///     hash: PHC-formatted hash string from hash_password()
///
/// Returns:
///     True if password matches, False otherwise
#[pyfunction]
pub fn verify_password(password: &str, hash: &str) -> PyResult<bool> {
    let parsed_hash = PasswordHash::new(hash).map_err(|e| {
        pyo3::exceptions::PyValueError::new_err(format!("Invalid hash format: {}", e))
    })?;

    Ok(Argon2::default()
        .verify_password(password.as_bytes(), &parsed_hash)
        .is_ok())
}

// ============================================================================
// CSRF Token Generation
// ============================================================================

/// Generate a cryptographically secure random token
///
/// Args:
///     length: Number of random bytes (default 32, result is hex-encoded = 64 chars)
///
/// Returns:
///     Hex-encoded random token string
#[pyfunction]
#[pyo3(signature = (length = 32))]
pub fn generate_token(length: usize) -> String {
    let mut rng = thread_rng();
    let bytes: Vec<u8> = (0..length).map(|_| rng.gen()).collect();
    hex_encode(&bytes)
}

/// Generate a CSRF token (alias for generate_token with 32 bytes)
#[pyfunction]
pub fn generate_csrf_token() -> String {
    generate_token(32)
}

fn hex_encode(bytes: &[u8]) -> String {
    const HEX_CHARS: &[u8; 16] = b"0123456789abcdef";
    let mut s = String::with_capacity(bytes.len() * 2);
    for byte in bytes {
        s.push(HEX_CHARS[(byte >> 4) as usize] as char);
        s.push(HEX_CHARS[(byte & 0x0f) as usize] as char);
    }
    s
}
