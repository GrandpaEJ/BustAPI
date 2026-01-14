use argon2::{
    password_hash::{rand_core::OsRng, PasswordHash, PasswordHasher, PasswordVerifier, SaltString},
    Argon2,
};
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
