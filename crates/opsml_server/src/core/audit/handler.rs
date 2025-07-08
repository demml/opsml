use crate::core::state::AppState;
use opsml_events::{
    event::{insert_space_name_record, log_audit_event},
    Event,
};
use std::sync::Arc;
use tokio::task;
use tokio_stream::StreamExt;
use tracing::{error, info};

pub struct AuditEventHandler {
    state: Arc<AppState>,
}

impl AuditEventHandler {
    pub fn new(state: Arc<AppState>) -> Self {
        Self { state }
    }

    pub async fn start(self) {
        let mut events = self.state.event_bus.subscribe();

        info!("Starting audit event handler");
        task::spawn(async move {
            while let Some(event) = events.next().await {
                match event {
                    Event::Audit(record) => {
                        if let Err(e) = log_audit_event(record, self.state.sql_client.clone()).await
                        {
                            error!("Failed to log audit event: {e}");
                        }
                    }
                    Event::SpaceName(record) => {
                        if let Err(e) =
                            insert_space_name_record(record, self.state.sql_client.clone()).await
                        {
                            error!("Failed to log space name event: {e}");
                        }
                    }
                }
            }
        });
    }
}
