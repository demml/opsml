use futures::Stream;
use tokio::sync::broadcast;
use tokio_stream::wrappers::BroadcastStream;
use tokio_stream::StreamExt;

use crate::types::AuditEvent;

use opsml_error::error::ServerError;
use opsml_sql::enums::client::SqlClientEnum;

use tracing::{debug, instrument};

use crate::types::Event;
use std::sync::Arc;
use tracing::error;

#[instrument(skip_all)]
pub async fn log_audit_event(
    record: AuditEvent,
    sql_client: Arc<SqlClientEnum>,
) -> Result<(), ServerError> {
    debug!("Logging audit event: {:?}", record);

    //sql_client
    //.insert_operation(username, access_type, access_location)
    //.await?;

    Ok(())
}

#[derive(Clone)]
pub struct EventBus {
    tx: broadcast::Sender<Event>,
}

impl EventBus {
    #[instrument(skip_all)]
    pub fn new(capacity: usize) -> Self {
        debug!("Creating EventBus with capacity: {}", capacity);
        let (tx, _) = broadcast::channel(capacity);
        Self { tx }
    }

    #[instrument(skip_all)]
    pub fn publish(&self, event: Event) {
        debug!("Publishing event: {:?}", event);
        let _ = self.tx.send(event);
    }

    pub fn subscribe(&self) -> impl Stream<Item = Event> {
        let rx = self.tx.subscribe();
        BroadcastStream::new(rx).filter_map(|result| result.ok())
    }
}
