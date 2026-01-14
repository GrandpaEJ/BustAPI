//! JWT (JSON Web Token) support for BustAPI
//!
//! Provides high-performance JWT encoding/decoding using the jsonwebtoken crate.

use jsonwebtoken::{
    decode, encode, errors::ErrorKind, Algorithm, DecodingKey, EncodingKey, Header, Validation,
};
use pyo3::prelude::*;
use pyo3::types::PyDict;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::time::{SystemTime, UNIX_EPOCH};

/// JWT Claims structure
#[derive(Debug, Serialize, Deserialize)]
struct Claims {
    /// Subject (usually user ID)
    sub: String,
    /// Expiration time (Unix timestamp)
    exp: u64,
    /// Issued at (Unix timestamp)
    iat: u64,
    /// Not before (Unix timestamp)
    nbf: u64,
    /// JWT ID (unique identifier)
    jti: Option<String>,
    /// Token type (access/refresh)
    #[serde(rename = "type")]
    token_type: Option<String>,
    /// Fresh token flag
    fresh: Option<bool>,
    /// Custom claims
    #[serde(flatten)]
    custom: HashMap<String, serde_json::Value>,
}

/// JWT Manager for encoding and decoding tokens
#[pyclass]
pub struct JWTManager {
    encoding_key: EncodingKey,
    decoding_key: DecodingKey,
    algorithm: Algorithm,
    access_token_expires: u64,  // seconds
    refresh_token_expires: u64, // seconds
}

#[pymethods]
impl JWTManager {
    /// Create a new JWT Manager
    ///
    /// Args:
    ///     secret_key: Secret key for signing tokens (min 32 bytes recommended)
    ///     algorithm: Algorithm to use (default: "HS256")
    ///     access_expires: Access token expiry in seconds (default: 900 = 15 min)
    ///     refresh_expires: Refresh token expiry in seconds (default: 2592000 = 30 days)
    #[new]
    #[pyo3(signature = (secret_key, algorithm = "HS256", access_expires = 900, refresh_expires = 2592000))]
    pub fn new(
        secret_key: &str,
        algorithm: &str,
        access_expires: u64,
        refresh_expires: u64,
    ) -> PyResult<Self> {
        if secret_key.len() < 16 {
            return Err(pyo3::exceptions::PyValueError::new_err(
                "Secret key must be at least 16 characters",
            ));
        }

        let algo = match algorithm.to_uppercase().as_str() {
            "HS256" => Algorithm::HS256,
            "HS384" => Algorithm::HS384,
            "HS512" => Algorithm::HS512,
            _ => {
                return Err(pyo3::exceptions::PyValueError::new_err(
                    "Unsupported algorithm. Use HS256, HS384, or HS512",
                ))
            }
        };

        let encoding_key = EncodingKey::from_secret(secret_key.as_bytes());
        let decoding_key = DecodingKey::from_secret(secret_key.as_bytes());

        Ok(JWTManager {
            encoding_key,
            decoding_key,
            algorithm: algo,
            access_token_expires: access_expires,
            refresh_token_expires: refresh_expires,
        })
    }

    /// Create an access token
    ///
    /// Args:
    ///     identity: User identity (usually user ID as string)
    ///     expires_delta: Optional custom expiry in seconds
    ///     fresh: Whether this is a fresh token (from login, not refresh)
    ///     claims: Optional additional claims as dict
    ///
    /// Returns:
    ///     JWT token string
    #[pyo3(signature = (identity, expires_delta = None, fresh = true, claims = None))]
    pub fn create_access_token(
        &self,
        identity: &str,
        expires_delta: Option<u64>,
        fresh: bool,
        claims: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<String> {
        let expires = expires_delta.unwrap_or(self.access_token_expires);
        self.create_token(identity, expires, "access", Some(fresh), claims)
    }

    /// Create a refresh token
    ///
    /// Args:
    ///     identity: User identity (usually user ID as string)
    ///     expires_delta: Optional custom expiry in seconds
    ///     claims: Optional additional claims as dict
    ///
    /// Returns:
    ///     JWT token string
    #[pyo3(signature = (identity, expires_delta = None, claims = None))]
    pub fn create_refresh_token(
        &self,
        identity: &str,
        expires_delta: Option<u64>,
        claims: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<String> {
        let expires = expires_delta.unwrap_or(self.refresh_token_expires);
        self.create_token(identity, expires, "refresh", None, claims)
    }

    /// Decode and verify a token
    ///
    /// Args:
    ///     token: JWT token string
    ///
    /// Returns:
    ///     Dict with claims on success
    ///
    /// Raises:
    ///     ValueError: If token is invalid or expired
    pub fn decode_token(&self, py: Python<'_>, token: &str) -> PyResult<Py<PyAny>> {
        let mut validation = Validation::new(self.algorithm);
        validation.validate_exp = true;
        validation.validate_nbf = true;

        match decode::<Claims>(token, &self.decoding_key, &validation) {
            Ok(token_data) => {
                let dict = PyDict::new(py);
                dict.set_item("sub", &token_data.claims.sub)?;
                dict.set_item("identity", &token_data.claims.sub)?;
                dict.set_item("exp", token_data.claims.exp)?;
                dict.set_item("iat", token_data.claims.iat)?;
                dict.set_item("nbf", token_data.claims.nbf)?;

                if let Some(jti) = &token_data.claims.jti {
                    dict.set_item("jti", jti)?;
                }
                if let Some(token_type) = &token_data.claims.token_type {
                    dict.set_item("type", token_type)?;
                }
                if let Some(fresh) = token_data.claims.fresh {
                    dict.set_item("fresh", fresh)?;
                }

                // Add custom claims
                for (key, value) in &token_data.claims.custom {
                    let py_value = json_to_pyobject(py, value)?;
                    dict.set_item(key, py_value)?;
                }

                Ok(dict.into())
            }
            Err(err) => {
                let msg = match err.kind() {
                    ErrorKind::ExpiredSignature => "Token has expired",
                    ErrorKind::InvalidSignature => "Invalid token signature",
                    ErrorKind::InvalidToken => "Invalid token format",
                    ErrorKind::ImmatureSignature => "Token not yet valid (nbf)",
                    _ => "Token validation failed",
                };
                Err(pyo3::exceptions::PyValueError::new_err(msg))
            }
        }
    }

    /// Verify a token without returning claims
    ///
    /// Returns:
    ///     True if valid, False otherwise
    pub fn verify_token(&self, token: &str) -> bool {
        let mut validation = Validation::new(self.algorithm);
        validation.validate_exp = true;
        validation.validate_nbf = true;

        decode::<Claims>(token, &self.decoding_key, &validation).is_ok()
    }

    /// Get the identity from a token (without full validation)
    ///
    /// This extracts the subject claim, useful for logging even with expired tokens.
    pub fn get_identity(&self, token: &str) -> PyResult<Option<String>> {
        let mut validation = Validation::new(self.algorithm);
        validation.validate_exp = false;
        validation.validate_nbf = false;
        validation.insecure_disable_signature_validation();

        match decode::<Claims>(token, &self.decoding_key, &validation) {
            Ok(token_data) => Ok(Some(token_data.claims.sub)),
            Err(_) => Ok(None),
        }
    }
}

impl JWTManager {
    fn create_token(
        &self,
        identity: &str,
        expires_seconds: u64,
        token_type: &str,
        fresh: Option<bool>,
        claims: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<String> {
        let now = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_secs();

        let mut custom = HashMap::new();

        // Convert Python dict to custom claims
        if let Some(py_claims) = claims {
            for (key, value) in py_claims.iter() {
                let key_str: String = key.extract()?;
                let json_value = pyobject_to_json(&value)?;
                custom.insert(key_str, json_value);
            }
        }

        let claims = Claims {
            sub: identity.to_string(),
            exp: now + expires_seconds,
            iat: now,
            nbf: now,
            jti: Some(generate_jti()),
            token_type: Some(token_type.to_string()),
            fresh,
            custom,
        };

        let header = Header::new(self.algorithm);

        encode(&header, &claims, &self.encoding_key).map_err(|e| {
            pyo3::exceptions::PyValueError::new_err(format!("JWT encode error: {}", e))
        })
    }
}

/// Generate a unique JWT ID
fn generate_jti() -> String {
    use rand::{thread_rng, Rng};
    let mut rng = thread_rng();
    let bytes: [u8; 16] = rng.gen();
    hex::encode(&bytes)
}

/// Convert serde_json::Value to PyObject
fn json_to_pyobject(py: Python<'_>, value: &serde_json::Value) -> PyResult<Py<PyAny>> {
    match value {
        serde_json::Value::Null => Ok(py.None()),
        serde_json::Value::Bool(b) => Ok((*b).into_pyobject(py)?.to_owned().into_any().unbind()),
        serde_json::Value::Number(n) => {
            if let Some(i) = n.as_i64() {
                Ok(i.into_pyobject(py)?.to_owned().into_any().unbind())
            } else if let Some(f) = n.as_f64() {
                Ok(f.into_pyobject(py)?.to_owned().into_any().unbind())
            } else {
                Ok(py.None())
            }
        }
        serde_json::Value::String(s) => Ok(s.into_pyobject(py)?.to_owned().into_any().unbind()),
        serde_json::Value::Array(arr) => {
            let list = pyo3::types::PyList::empty(py);
            for item in arr {
                list.append(json_to_pyobject(py, item)?)?;
            }
            Ok(list.into())
        }
        serde_json::Value::Object(obj) => {
            let dict = PyDict::new(py);
            for (k, v) in obj {
                dict.set_item(k, json_to_pyobject(py, v)?)?;
            }
            Ok(dict.into())
        }
    }
}

/// Convert PyObject to serde_json::Value
fn pyobject_to_json(obj: &Bound<'_, pyo3::PyAny>) -> PyResult<serde_json::Value> {
    if obj.is_none() {
        Ok(serde_json::Value::Null)
    } else if let Ok(b) = obj.extract::<bool>() {
        Ok(serde_json::Value::Bool(b))
    } else if let Ok(i) = obj.extract::<i64>() {
        Ok(serde_json::json!(i))
    } else if let Ok(f) = obj.extract::<f64>() {
        Ok(serde_json::json!(f))
    } else if let Ok(s) = obj.extract::<String>() {
        Ok(serde_json::Value::String(s))
    } else if let Ok(list) = obj.cast::<pyo3::types::PyList>() {
        let mut arr = Vec::new();
        for item in list.iter() {
            arr.push(pyobject_to_json(&item)?);
        }
        Ok(serde_json::Value::Array(arr))
    } else if let Ok(dict) = obj.cast::<PyDict>() {
        let mut map = serde_json::Map::new();
        for (k, v) in dict.iter() {
            let key: String = k.extract()?;
            map.insert(key, pyobject_to_json(&v)?);
        }
        Ok(serde_json::Value::Object(map))
    } else {
        // Fallback to string representation
        Ok(serde_json::Value::String(obj.str()?.to_string()))
    }
}

// We need hex for jti generation
mod hex {
    const HEX_CHARS: &[u8; 16] = b"0123456789abcdef";

    pub fn encode(bytes: &[u8]) -> String {
        let mut s = String::with_capacity(bytes.len() * 2);
        for byte in bytes {
            s.push(HEX_CHARS[(byte >> 4) as usize] as char);
            s.push(HEX_CHARS[(byte & 0x0f) as usize] as char);
        }
        s
    }
}
