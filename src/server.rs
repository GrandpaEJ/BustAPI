//! HTTP Server implementation using Tokio and Hyper

use crate::router::Router;
use anyhow::Result;
use hyper::server::conn::http1;
use hyper::service::service_fn;
use hyper::Request;
use hyper_util::rt::TokioIo;
use std::net::SocketAddr;
use std::sync::Arc;
use tokio::net::TcpListener;
use tracing::{error, info};

/// Configuration for the BustAPI server
#[derive(Debug, Clone)]
pub struct ServerConfig {
    pub host: String,
    pub port: u16,
    pub debug: bool,
}

impl Default for ServerConfig {
    fn default() -> Self {
        Self {
            host: "127.0.0.1".to_string(),
            port: 5000,
            debug: false,
        }
    }
}

/// Main HTTP server struct
#[derive(Clone)]
pub struct BustServer {
    router: Arc<Router>,
    config: ServerConfig,
}

impl BustServer {
    /// Create a new server instance
    pub fn new() -> Self {
        Self {
            router: Arc::new(Router::new()),
            config: ServerConfig::default(),
        }
    }

    /// Create a new server with custom configuration
    pub fn with_config(config: ServerConfig) -> Self {
        Self {
            router: Arc::new(Router::new()),
            config,
        }
    }

    /// Get a mutable reference to the router
    pub fn router_mut(&mut self) -> &mut Router {
        Arc::get_mut(&mut self.router).expect("Router should be mutable")
    }

    /// Get router reference
    pub fn router(&self) -> &Router {
        &self.router
    }

    /// Set server configuration
    pub fn set_config(&mut self, config: ServerConfig) {
        self.config = config;
    }

    /// Get server configuration
    pub fn config(&self) -> &ServerConfig {
        &self.config
    }

    /// Start the server
    pub async fn serve(&self) -> Result<()> {
        let addr: SocketAddr = format!("{}:{}", self.config.host, self.config.port).parse()?;
        let listener = TcpListener::bind(addr).await?;

        info!("BustAPI server starting on http://{}", addr);

        let router = Arc::clone(&self.router);

        loop {
            let (stream, _) = listener.accept().await?;
            let io = TokioIo::new(stream);
            let router = Arc::clone(&router);

            tokio::task::spawn(async move {
                if let Err(err) = http1::Builder::new()
                    .serve_connection(
                        io,
                        service_fn(move |req: Request<hyper::body::Incoming>| {
                            let router = Arc::clone(&router);
                            async move { router.handle_request(req).await }
                        }),
                    )
                    .await
                {
                    error!("Error serving connection: {:?}", err);
                }
            });
        }
    }

    /// Start the server with graceful shutdown
    pub async fn serve_with_shutdown(&self) -> Result<()> {
        let addr: SocketAddr = format!("{}:{}", self.config.host, self.config.port).parse()?;
        let listener = TcpListener::bind(addr).await?;

        info!("BustAPI server starting on http://{}", addr);

        let router = Arc::clone(&self.router);

        // Handle shutdown signal
        let shutdown_signal = async {
            tokio::signal::ctrl_c()
                .await
                .expect("Failed to install CTRL+C signal handler");
            info!("Received shutdown signal, gracefully shutting down server...");
        };

        tokio::select! {
            _ = async {
                loop {
                    let (stream, _) = listener.accept().await?;
                    let io = TokioIo::new(stream);
                    let router = Arc::clone(&router);

                    tokio::task::spawn(async move {
                        if let Err(err) = http1::Builder::new()
                            .serve_connection(
                                io,
                                service_fn(move |req: Request<hyper::body::Incoming>| {
                                    let router = Arc::clone(&router);
                                    async move { router.handle_request(req).await }
                                }),
                            )
                            .await
                        {
                            error!("Error serving connection: {:?}", err);
                        }
                    });
                }
                #[allow(unreachable_code)]
                Ok::<(), anyhow::Error>(())
            } => {}
            _ = shutdown_signal => {
                info!("Server shutdown complete");
            }
        }

        Ok(())
    }
}

impl Default for BustServer {
    fn default() -> Self {
        Self::new()
    }
}
