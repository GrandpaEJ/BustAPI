use crate::response::ResponseData;
use http::StatusCode;
use std::fs::{self, File};
use std::io::{Read, Seek, SeekFrom};
use std::path::Path;

/// Parse Range header: bytes=start-end
pub fn parse_range_header(range_header: &str, file_size: u64) -> Option<(u64, u64)> {
    if !range_header.starts_with("bytes=") {
        return None;
    }

    let range_val = &range_header["bytes=".len()..];
    let parts: Vec<&str> = range_val.split('-').collect();

    if parts.is_empty() {
        return None;
    }

    let start_str = parts[0];
    let end_str = if parts.len() > 1 { parts[1] } else { "" };

    let start = if start_str.is_empty() {
        // Suffix byte range: bytes=-500 (last 500 bytes) - Not fully supported
        0
    } else {
        start_str.parse::<u64>().unwrap_or(0)
    };

    let end = if end_str.is_empty() {
        file_size - 1
    } else {
        end_str.parse::<u64>().unwrap_or(file_size - 1)
    };

    if start > end || start >= file_size {
        return None;
    }

    Some((start, std::cmp::min(end, file_size - 1)))
}

/// Serve a file, potentially with a partial range
pub fn serve_file_part(path: &Path, range_header: Option<&String>) -> ResponseData {
    if !path.exists() || !path.is_file() {
         return ResponseData::error(StatusCode::NOT_FOUND, Some("File Not Found"));
    }

    let mime_type = mime_guess::from_path(path).first_or_octet_stream();
    let file_size = match fs::metadata(path) {
        Ok(meta) => meta.len(),
        Err(_) => return ResponseData::error(StatusCode::INTERNAL_SERVER_ERROR, Some("File Meta Error")),
    };

    // Check for Range Header
    if let Some(range_h) = range_header {
        if let Some((start, end)) = parse_range_header(range_h, file_size) {
            // Partial Content
            let length = end - start + 1;
            let mut file = match File::open(path) {
                Ok(f) => f,
                Err(_) => return ResponseData::error(StatusCode::INTERNAL_SERVER_ERROR, Some("File Open Error")),
            };

            if let Err(_) = file.seek(SeekFrom::Start(start)) {
                return ResponseData::error(StatusCode::INTERNAL_SERVER_ERROR, Some("File Seek Error"));
            }

            let mut buffer = vec![0u8; length as usize];
            if let Err(_) = file.read_exact(&mut buffer) {
                return ResponseData::error(StatusCode::INTERNAL_SERVER_ERROR, Some("File Read Error"));
            }

            let mut resp = ResponseData::with_body(buffer);
            resp.status = StatusCode::PARTIAL_CONTENT;
            resp.set_header("Content-Type", mime_type.as_ref());
            resp.set_header("Content-Range", &format!("bytes {}-{}/{}", start, end, file_size));
            resp.set_header("Content-Length", &length.to_string());
            resp.set_header("Accept-Ranges", "bytes");
            return resp;
        }
    }

    // Full Content
    match fs::read(path) {
        Ok(content) => {
            let mut resp = ResponseData::with_body(content);
            resp.set_header("Content-Type", mime_type.as_ref());
            resp.set_header("Content-Length", &file_size.to_string());
            resp.set_header("Accept-Ranges", "bytes");
            return resp;
        }
        Err(_) => {
            return ResponseData::error(
                StatusCode::INTERNAL_SERVER_ERROR,
                Some("File Access Error"),
            )
        }
    }
}
