use chrono::Local;
use colored::*;
use pyo3::prelude::*;

#[pyclass(name = "FastLogger")]
pub struct PyFastLogger;

#[pymethods]
impl PyFastLogger {
    #[new]
    fn new() -> Self {
        PyFastLogger
    }

    fn log_request(&self, method: &str, path: &str, status: u16, duration: f64) {
        // Format timestamp
        let now = Local::now();
        let timestamp = now.format("%H:%M:%S").to_string();
        let timestamp_colored = timestamp.white();

        // Format method
        let method_colored = match method {
            "GET" => method.blue(),
            "POST" => method.green(),
            "PUT" => method.yellow(),
            "DELETE" => method.red(),
            "PATCH" => method.cyan(),
            "HEAD" => method.magenta(),
            "OPTIONS" => method.white(),
            _ => method.normal(),
        };

        // Format status
        let status_colored = if status >= 500 {
            status.to_string().red()
        } else if status >= 400 {
            status.to_string().yellow()
        } else if status >= 300 {
            status.to_string().cyan()
        } else if status >= 200 {
            status.to_string().green()
        } else {
            status.to_string().white()
        };

        // Format duration
        let duration_str = if duration >= 1.0 {
            format!("{:.3}s", duration)
        } else if duration >= 0.001 {
            format!("{:.3}ms", duration * 1000.0)
        } else if duration >= 0.000001 {
            format!("{:.3}μs", duration * 1_000_000.0)
        } else {
            format!("{:.3}ns", duration * 1_000_000_000.0)
        };

        let duration_colored = duration_str.white();

        // Format: TIME | STATUS | LATENCY | METHOD | PATH
        println!(
            "{} | {:<7} | {:<10} | {:<7} | {}",
            timestamp_colored, status_colored, duration_colored, method_colored, path
        );
    }
}
