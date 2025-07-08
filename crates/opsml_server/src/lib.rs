pub mod core;

use crate::core::app::create_app;
use opsml_colors::Colorize;
use std::net::SocketAddr;
use std::sync::Arc;
use tokio::sync::Mutex;
use tokio::task::JoinHandle;
use tracing::info;

pub async fn start_server() -> Result<(), Box<dyn std::error::Error>> {
    let logo = r#"
         ____             __  _____       _____                          
        / __ \____  _____/  |/  / /      / ___/___  ______   _____  _____
       / / / / __ \/ ___/ /|_/ / /       \__ \/ _ \/ ___/ | / / _ \/ ___/
      / /_/ / /_/ (__  ) /  / / /___    ___/ /  __/ /   | |/ /  __/ /    
      \____/ .___/____/_/  /_/_____/   /____/\___/_/    |___/\___/_/     
          /_/                                                            
                   
        "#;

    println!("{}", Colorize::green(logo));

    // build our application with routes
    let app = create_app().await.unwrap();

    // get OPSML_SERVER_PORT from env
    let port = std::env::var("OPSML_SERVER_PORT").unwrap_or_else(|_| "3000".to_string());
    let addr = format!("0.0.0.0:{port}");

    // run it
    let listener = tokio::net::TcpListener::bind(addr).await.unwrap();

    info!("listening on {}", listener.local_addr().unwrap());

    println!("🚀 Server Running 🚀");

    axum::serve(
        listener,
        app.into_make_service_with_connect_info::<SocketAddr>(),
    )
    .await
    .unwrap();

    Ok(())
}

pub fn start_server_in_background() -> Arc<Mutex<Option<JoinHandle<()>>>> {
    let handle = Arc::new(Mutex::new(None));
    let handle_clone = handle.clone();

    tokio::spawn(async move {
        let server_handle = tokio::spawn(async {
            if let Err(e) = start_server().await {
                eprintln!("Server error: {e}");
            }
        });

        *handle_clone.lock().await = Some(server_handle);
    });

    handle
}

pub async fn stop_server(handle: Arc<Mutex<Option<JoinHandle<()>>>>) {
    if let Some(handle) = handle.lock().await.take() {
        handle.abort();
        info!("Server stopped");
    }
}
