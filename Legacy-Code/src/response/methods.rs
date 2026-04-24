//! Response methods

use super::builders::ResponseData;
use actix_web::http::StatusCode;

impl ResponseData {
    /// Set response status
    pub fn set_status(&mut self, status: StatusCode) -> &mut Self {
        self.status = status;
        self
    }

    /// Set response body
    pub fn set_body<B: Into<Vec<u8>>>(&mut self, body: B) -> &mut Self {
        self.body = body.into();
        self
    }

    /// Set header value
    pub fn set_header<K: Into<String>, V: Into<String>>(&mut self, key: K, value: V) -> &mut Self {
        self.headers.insert(key.into(), value.into());
        self
    }

    /// Get header value
    pub fn get_header(&self, key: &str) -> Option<&String> {
        self.headers.get(key)
    }

    /// Get response body as string
    pub fn body_as_string(&self) -> Result<String, std::string::FromUtf8Error> {
        String::from_utf8(self.body.clone())
    }

    /// Check if response is successful (2xx status)
    pub fn is_success(&self) -> bool {
        self.status.is_success()
    }

    /// Get content length
    pub fn content_length(&self) -> usize {
        self.body.len()
    }
}
