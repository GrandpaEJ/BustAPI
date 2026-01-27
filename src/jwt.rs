//! JWT (JSON Web Token) support for BustAPI
//!
//! Provides high-performance JWT encoding/decoding using pure Rust crates (hmac, sha2, base64).
//! Removing `ring` dependency to fix cross-compilation issues.

use base64::{engine::general_purpose::URL_SAFE_NO_PAD, Engine as _};
use hmac::{Hmac, Mac};
use pyo3::prelude::*;
use pyo3::types::PyDict;
use serde::{Deserialize, Serialize};
use sha2::{Sha256, Sha384, Sha512};
use std::collections::HashMap;
use std::time::{SystemTime, UNIX_EPOCH};

type HmacSha256 = Hmac<Sha256>;
type HmacSha384 = Hmac<Sha384>;
type HmacSha512 = Hmac<Sha512>;

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
    #[serde(skip_serializing_if = "Option::is_none")]
    jti: Option<String>,
    /// Token type (access/refresh)
    #[serde(rename = "type")]
    #[serde(skip_serializing_if = "Option::is_none")]
    token_type: Option<String>,
    /// Fresh token flag
    #[serde(skip_serializing_if = "Option::is_none")]
    fresh: Option<bool>,
    /// Custom claims
    #[serde(flatten)]
    custom: HashMap<String, serde_json::Value>,
}

#[derive(Debug, Serialize, Deserialize)]
struct Header {
    alg: String,
    typ: String,
}

impl Header {
    fn new(alg: &str) -> Self {
        Self {
            alg: alg.to_string(),
            typ: "JWT".to_string(),
        }
    }
}

/// JWT Manager for encoding and decoding tokens
#[pyclass]
pub struct JWTManager {
    secret_key: String,
    _algorithm: String,         // Only HS256 supported for now
    access_token_expires: u64,  // seconds
    refresh_token_expires: u64, // seconds
}

#[pymethods]
impl JWTManager {
    /// Create a new JWT Manager
    ///
    /// Args:
    ///     secret_key: Secret key for signing tokens (min 16 chars recommended)
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

        let algo = algorithm.to_uppercase();
        if !["HS256", "HS384", "HS512"].contains(&algo.as_str()) {
            return Err(pyo3::exceptions::PyValueError::new_err(
                "Unsupported algorithm. Use HS256, HS384, or HS512",
            ));
        }

        Ok(JWTManager {
            secret_key: secret_key.to_string(),
            _algorithm: algo,
            access_token_expires: access_expires,
            refresh_token_expires: refresh_expires,
        })
    }

    /// Create an access token
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
    pub fn decode_token(&self, py: Python<'_>, token: &str) -> PyResult<Py<PyAny>> {
        let claims = self.verify_and_decode(token)?;

        let dict = PyDict::new(py);
        dict.set_item("sub", &claims.sub)?;
        dict.set_item("identity", &claims.sub)?; // Alias for convenience
        dict.set_item("exp", claims.exp)?;
        dict.set_item("iat", claims.iat)?;
        dict.set_item("nbf", claims.nbf)?;

        if let Some(jti) = &claims.jti {
            dict.set_item("jti", jti)?;
        }
        if let Some(token_type) = &claims.token_type {
            dict.set_item("type", token_type)?;
        }
        if let Some(fresh) = claims.fresh {
            dict.set_item("fresh", fresh)?;
        }

        // Add custom claims
        for (key, value) in &claims.custom {
            let py_value = json_to_pyobject(py, value)?;
            dict.set_item(key, py_value)?;
        }

        Ok(dict.into())
    }

    /// Verify a token without returning claims
    pub fn verify_token(&self, token: &str) -> bool {
        self.verify_and_decode(token).is_ok()
    }

    /// Get the identity from a token (without full validation/signature check)
    /// WARNING: This does NOT verify the signature. Use only for non-security critical checks.
    pub fn get_identity(&self, token: &str) -> PyResult<Option<String>> {
        let parts: Vec<&str> = token.split('.').collect();
        if parts.len() != 3 {
            return Ok(None);
        }

        // Decode payload (2nd part)
        let payload_json = match decode_b64(parts[1]) {
            Ok(v) => v,
            Err(_) => return Ok(None),
        };

        let claims: serde_json::Value = match serde_json::from_slice(&payload_json) {
            Ok(v) => v,
            Err(_) => return Ok(None),
        };

        if let Some(sub) = claims.get("sub").and_then(|v| v.as_str()) {
            Ok(Some(sub.to_string()))
        } else {
            Ok(None)
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

        let header = Header::new(&self._algorithm);

        // Serialize
        let header_json = serde_json::to_string(&header).map_err(py_err)?;
        let claims_json = serde_json::to_string(&claims).map_err(py_err)?;

        // Base64 Encode
        let header_b64 = encode_b64(header_json.as_bytes());
        let claims_b64 = encode_b64(claims_json.as_bytes());

        // Sign
        let signing_input = format!("{}.{}", header_b64, claims_b64);
        let signature = self.sign(&signing_input)?;
        let signature_b64 = encode_b64(&signature);

        Ok(format!("{}.{}", signing_input, signature_b64))
    }

    fn sign(&self, input: &str) -> PyResult<Vec<u8>> {
        match self._algorithm.as_str() {
            "HS256" => {
                let mut mac = HmacSha256::new_from_slice(self.secret_key.as_bytes()).map_err(|_| {
                    pyo3::exceptions::PyValueError::new_err("Invalid key length")
                })?;
                mac.update(input.as_bytes());
                Ok(mac.finalize().into_bytes().to_vec())
            }
            "HS384" => {
                let mut mac = HmacSha384::new_from_slice(self.secret_key.as_bytes()).map_err(|_| {
                    pyo3::exceptions::PyValueError::new_err("Invalid key length")
                })?;
                mac.update(input.as_bytes());
                Ok(mac.finalize().into_bytes().to_vec())
            }
            "HS512" => {
                let mut mac = HmacSha512::new_from_slice(self.secret_key.as_bytes()).map_err(|_| {
                    pyo3::exceptions::PyValueError::new_err("Invalid key length")
                })?;
                mac.update(input.as_bytes());
                Ok(mac.finalize().into_bytes().to_vec())
            }
            _ => Err(pyo3::exceptions::PyValueError::new_err("Unsupported algorithm")),
        }
    }

    fn verify_and_decode(&self, token: &str) -> PyResult<Claims> {
        let parts: Vec<&str> = token.split('.').collect();
        if parts.len() != 3 {
            return Err(pyo3::exceptions::PyValueError::new_err(
                "Invalid token format",
            ));
        }

        let header_b64 = parts[0];
        let claims_b64 = parts[1];
        let signature_b64 = parts[2];

        // 1. Verify Signature
        let signing_input = format!("{}.{}", header_b64, claims_b64);
        let provided_sig = decode_b64(signature_b64)
            .map_err(|_| pyo3::exceptions::PyValueError::new_err("Invalid signature encoding"))?;

        // Constant time comparison
        // Using verify_slice is safer
        let verification_result = match self._algorithm.as_str() {
            "HS256" => {
                let mut mac = HmacSha256::new_from_slice(self.secret_key.as_bytes()).map_err(|_| {
                    pyo3::exceptions::PyValueError::new_err("Invalid key")
                })?;
                mac.update(signing_input.as_bytes());
                mac.verify_slice(&provided_sig)
            }
            "HS384" => {
                let mut mac = HmacSha384::new_from_slice(self.secret_key.as_bytes()).map_err(|_| {
                    pyo3::exceptions::PyValueError::new_err("Invalid key")
                })?;
                mac.update(signing_input.as_bytes());
                mac.verify_slice(&provided_sig)
            }
            "HS512" => {
                let mut mac = HmacSha512::new_from_slice(self.secret_key.as_bytes()).map_err(|_| {
                    pyo3::exceptions::PyValueError::new_err("Invalid key")
                })?;
                mac.update(signing_input.as_bytes());
                mac.verify_slice(&provided_sig)
            }
            _ => return Err(pyo3::exceptions::PyValueError::new_err("Unsupported algorithm")),
        };

        if verification_result.is_err() {
            return Err(pyo3::exceptions::PyValueError::new_err("Invalid signature"));
        }

        // 2. Decode Claims
        let claims_json = decode_b64(claims_b64)
            .map_err(|_| pyo3::exceptions::PyValueError::new_err("Invalid claims encoding"))?;
        let claims: Claims = serde_json::from_slice(&claims_json)
            .map_err(|_| pyo3::exceptions::PyValueError::new_err("Invalid claims JSON"))?;

        // 3. Validate Expiration
        let now = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_secs();

        if claims.exp < now {
            return Err(pyo3::exceptions::PyValueError::new_err("Token has expired"));
        }

        // 4. Validate Not Before
        if claims.nbf > now + 10 {
            // 10s leeway
            return Err(pyo3::exceptions::PyValueError::new_err(
                "Token not yet valid",
            ));
        }

        Ok(claims)
    }
}

fn encode_b64(input: &[u8]) -> String {
    URL_SAFE_NO_PAD.encode(input)
}

fn decode_b64(input: &str) -> Result<Vec<u8>, base64::DecodeError> {
    URL_SAFE_NO_PAD.decode(input)
}

fn py_err<E: std::fmt::Display>(err: E) -> PyErr {
    pyo3::exceptions::PyValueError::new_err(format!("{}", err))
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
