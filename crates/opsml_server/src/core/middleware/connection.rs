use axum::{
    body::Body,
    extract::{ConnectInfo, State},
    http::Request,
    middleware::Next,
    response::Response,
};
use std::{
    collections::HashMap,
    net::SocketAddr,
    sync::{
        atomic::{AtomicUsize, Ordering},
        Arc, Mutex,
    },
    time::{Duration, Instant, SystemTime, UNIX_EPOCH},
};
use tokio::time::interval;
use tracing::{debug, warn};

#[derive(Debug, Clone)]
pub struct ConnectionInfo {
    pub remote_addr: SocketAddr,
    pub connected_at: Instant,
    pub request_count: Arc<AtomicUsize>,
    pub last_request_at: Arc<Mutex<Instant>>,
    pub user_agent: Option<String>,
    pub path: String,
    pub method: String,
    pub connection_type: ConnectionType,
}

#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub enum ConnectionType {
    Api,
    SpaStatic,
    SpaIndex,
    Health,
    Unknown,
}

impl ConnectionType {
    fn from_path(path: &str) -> Self {
        match path {
            p if p.starts_with("/opsml/api") => Self::Api,
            p if p.starts_with("/health") => Self::Health,
            "/" | "/index.html" => Self::SpaIndex,
            p if p.ends_with(".js")
                || p.ends_with(".css")
                || p.ends_with(".wasm")
                || p.ends_with(".ico")
                || p.ends_with(".png")
                || p.ends_with(".svg") =>
            {
                Self::SpaStatic
            }
            _ => Self::Unknown,
        }
    }
}

#[derive(Clone)]
pub struct ConnectionTracker {
    connections: Arc<Mutex<HashMap<String, ConnectionInfo>>>,
    total_connections: Arc<AtomicUsize>,
    peak_connections: Arc<AtomicUsize>,
    api_connections: Arc<AtomicUsize>,
    spa_connections: Arc<AtomicUsize>,
    request_counter: Arc<AtomicUsize>, // Add a request counter for unique IDs
}

impl ConnectionTracker {
    pub fn new() -> Self {
        let tracker = Self {
            connections: Arc::new(Mutex::new(HashMap::new())),
            total_connections: Arc::new(AtomicUsize::new(0)),
            peak_connections: Arc::new(AtomicUsize::new(0)),
            api_connections: Arc::new(AtomicUsize::new(0)),
            spa_connections: Arc::new(AtomicUsize::new(0)),
            request_counter: Arc::new(AtomicUsize::new(0)),
        };

        // Start background task to log connection stats and cleanup stale connections
        let tracker_clone = tracker.clone();
        tokio::spawn(async move {
            debug!("Starting connection tracker background task");
            let mut interval = interval(Duration::from_secs(30));
            loop {
                interval.tick().await;
                tracker_clone.log_connection_stats().await;
                tracker_clone.cleanup_stale_connections().await;
            }
        });

        tracker
    }

    pub async fn track_connection(&self, req: Request<Body>) -> (Request<Body>, String) {
        let connect_info = req.extensions().get::<ConnectInfo<SocketAddr>>();
        let remote_addr = connect_info
            .map(|ci| ci.0)
            .unwrap_or_else(|| "0.0.0.0:0".parse().unwrap());

        let user_agent = req
            .headers()
            .get("user-agent")
            .and_then(|ua| ua.to_str().ok())
            .map(|s| s.to_string());

        let path = req.uri().path().to_string();
        let method = req.method().to_string();
        let connection_type = ConnectionType::from_path(&path);

        // Create unique connection ID using timestamp and atomic counter
        let request_id = self.request_counter.fetch_add(1, Ordering::Relaxed);
        let timestamp = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap_or_default()
            .as_nanos();

        let connection_id = format!(
            "{}:{}:{}:{}",
            remote_addr,
            std::process::id(),
            timestamp,
            request_id
        );

        let mut connections = self.connections.lock().unwrap();

        // Create a new entry for each request to track concurrent requests
        let conn_info = ConnectionInfo {
            remote_addr,
            connected_at: Instant::now(),
            request_count: Arc::new(AtomicUsize::new(1)),
            last_request_at: Arc::new(Mutex::new(Instant::now())),
            user_agent: user_agent.clone(),
            path: path.clone(),
            method: method.clone(),
            connection_type: connection_type.clone(),
        };

        connections.insert(connection_id.clone(), conn_info);
        let current_count = self.total_connections.fetch_add(1, Ordering::Relaxed) + 1;

        // Update type-specific counters
        match connection_type {
            ConnectionType::Api => {
                self.api_connections.fetch_add(1, Ordering::Relaxed);
            }
            ConnectionType::SpaStatic | ConnectionType::SpaIndex => {
                self.spa_connections.fetch_add(1, Ordering::Relaxed);
            }
            _ => {}
        }

        // Update peak if necessary
        let mut peak = self.peak_connections.load(Ordering::Relaxed);
        while current_count > peak {
            match self.peak_connections.compare_exchange_weak(
                peak,
                current_count,
                Ordering::Relaxed,
                Ordering::Relaxed,
            ) {
                Ok(_) => break,
                Err(new_peak) => peak = new_peak,
            }
        }

        debug!(
            "New request: {} | {} {} | Type: {:?} | From: {} | User-Agent: {} | Active: {}",
            connection_id,
            method,
            path,
            connection_type,
            remote_addr,
            user_agent.as_deref().unwrap_or("Unknown"),
            current_count
        );

        (req, connection_id)
    }

    pub async fn release_connection(&self, connection_id: &str) {
        let mut connections = self.connections.lock().unwrap();
        if let Some(conn_info) = connections.remove(connection_id) {
            let current_count = self.total_connections.fetch_sub(1, Ordering::Relaxed) - 1;

            // Update type-specific counters
            match conn_info.connection_type {
                ConnectionType::Api => {
                    self.api_connections.fetch_sub(1, Ordering::Relaxed);
                }
                ConnectionType::SpaStatic | ConnectionType::SpaIndex => {
                    self.spa_connections.fetch_sub(1, Ordering::Relaxed);
                }
                _ => {}
            }

            debug!(
                "Request completed: {} | Duration: {:?} | Type: {:?} | Active: {}",
                connection_id,
                conn_info.connected_at.elapsed(),
                conn_info.connection_type,
                current_count
            );
        }
    }

    // ...rest of the methods remain the same...
    pub async fn log_connection_stats(&self) {
        let connections = self.connections.lock().unwrap();
        let active_count = connections.len();
        let peak = self.peak_connections.load(Ordering::Relaxed);
        let api_count = self.api_connections.load(Ordering::Relaxed);
        let spa_count = self.spa_connections.load(Ordering::Relaxed);

        if active_count > 0 {
            debug!("=== Connection Stats ===");
            debug!("Total active connections: {}", active_count);
            debug!("API connections: {}", api_count);
            debug!("SPA connections: {}", spa_count);
            debug!("Peak connections: {}", peak);

            // Group by connection type
            let mut type_stats: HashMap<ConnectionType, usize> = HashMap::new();
            let mut ua_stats: HashMap<String, usize> = HashMap::new();
            let mut long_lived_connections = 0;

            for (id, conn) in connections.iter() {
                *type_stats.entry(conn.connection_type.clone()).or_insert(0) += 1;

                let ua = conn.user_agent.as_deref().unwrap_or("Unknown").to_string();
                *ua_stats.entry(ua).or_insert(0) += 1;

                // Check for long-lived connections (> 30 seconds for HTTP requests is unusual)
                if conn.connected_at.elapsed() > Duration::from_secs(30) {
                    long_lived_connections += 1;
                    warn!(
                        "Long-lived request: {} | {} {} | Duration: {:?} | Type: {:?}",
                        id,
                        conn.method,
                        conn.path,
                        conn.connected_at.elapsed(),
                        conn.connection_type
                    );
                }
            }

            debug!("Connections by Type:");
            for (conn_type, count) in type_stats {
                debug!("  {:?}: {}", conn_type, count);
            }

            debug!("Top User-Agents:");
            for (ua, count) in ua_stats.iter().take(5) {
                debug!("  {}: {}", ua, count);
            }

            if long_lived_connections > 0 {
                warn!(
                    "Long-lived requests detected: {} (this might indicate stuck connections)",
                    long_lived_connections
                );
            }

            debug!("=== End Stats ===");
        }
    }

    pub async fn cleanup_stale_connections(&self) {
        let mut connections = self.connections.lock().unwrap();
        let stale_threshold = Duration::from_secs(120); // 2 minutes for HTTP requests

        let stale_connections: Vec<String> = connections
            .iter()
            .filter(|(_, conn)| conn.connected_at.elapsed() > stale_threshold)
            .map(|(id, _)| id.clone())
            .collect();

        for id in stale_connections {
            if let Some(conn_info) = connections.remove(&id) {
                self.total_connections.fetch_sub(1, Ordering::Relaxed);

                // Update type-specific counters
                match conn_info.connection_type {
                    ConnectionType::Api => {
                        self.api_connections.fetch_sub(1, Ordering::Relaxed);
                    }
                    ConnectionType::SpaStatic | ConnectionType::SpaIndex => {
                        self.spa_connections.fetch_sub(1, Ordering::Relaxed);
                    }
                    _ => {}
                }

                warn!(
                    "Cleaned up stale request: {} | Type: {:?}",
                    id, conn_info.connection_type
                );
            }
        }
    }
}

/// Middleware function to track connections
pub async fn connection_tracking_middleware(
    State(tracker): State<Arc<ConnectionTracker>>,
    req: Request<Body>,
    next: Next,
) -> Response {
    let (req, connection_id) = tracker.track_connection(req).await;
    let response = next.run(req).await;
    tracker.release_connection(&connection_id).await;

    response
}
