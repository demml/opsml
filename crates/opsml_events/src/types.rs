use futures::Stream;
use tokio::sync::broadcast;
use tokio_stream::wrappers::BroadcastStream;
use tokio_stream::StreamExt;

use crate::event::AuditEvent;
use tracing::{debug, instrument};

#[derive(Debug, Clone)]
pub enum Event {
    Audit(AuditEvent),
    // Add other events as needed
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
