use tokio::signal;
use tracing::info;

pub async fn shutdown_service_signal(service_name: &str) {
    let ctrl_c = async {
        signal::ctrl_c()
            .await
            .expect("failed to install Ctrl+C handler");
    };

    #[cfg(unix)]
    let terminate = async {
        signal::unix::signal(signal::unix::SignalKind::terminate())
            .expect("failed to install signal handler")
            .recv()
            .await;
    };

    #[cfg(not(unix))]
    let terminate = std::future::pending::<()>();

    tokio::select! {
        _ = ctrl_c => {
            info!("{service_name}: Received SIGINT");
            info!("{service_name}: Exiting immediately");
        },
        _ = terminate => {
            info!("{service_name}: Received SIGINT");
            info!("{service_name}: Exiting immediately");
        },
    }
}
