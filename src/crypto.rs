use cookie::{Cookie, CookieJar, Key};
use pyo3::prelude::*;
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
}
