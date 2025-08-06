# Technical Component Specification: EventBus

## Overview
The `EventBus` serves as a central event system to be used with the OpsML server to record events. It provides asynchronous event distribution using Tokio's broadcast channel, and it enables decoupled communication between different parts of the system, particularly for audit logging and monitoring.

## Component Definition

````rust
#[derive(Clone)]
pub struct EventBus {
    tx: broadcast::Sender<Event>,
}

pub enum Event {
    Audit(AuditEvent),
    // Extensible for future event types
}
````

## Core Responsibilities

1. **Event Distribution**

      - Asynchronous event broadcasting
      - Multiple subscriber support
      - Non-blocking event publishing
      - Event type management

2. **Stream Management**
      - Stream-based event subscription
      - Automatic error filtering
      - Broadcast channel capacity control
      - Subscriber lifecycle management

3. **Event Type Handling**
      - Support for different event types
      - Type-safe event distribution
      - Event filtering capabilities
      - Extensible event system
  
## Use Cases
- **Audit Logging**: Capture and record system events for auditing purposes.

## Key Methods

### Constructor
````rust
pub fn new(capacity: usize) -> Self {
    let (tx, _) = broadcast::channel(capacity);
    Self { tx }
}
````

### Core Operations
````rust
pub fn publish(&self, event: Event)
pub fn subscribe(&self) -> impl Stream<Item = Event>
````

## Dependencies

- **External Crates**
    - `tokio`: Async runtime and broadcast channel
    - `futures`: Stream trait implementations
    - `tokio-stream`: Stream wrappers
    - `tracing`: Logging and instrumentation

- **Internal Components**
    - `Event`: Event type enum
    - `AuditEvent`: Audit event structure
    - `EventError`: Error handling

## Error Handling

  - Silent error handling for send operations
  - Stream filtering for failed receives
  - Debug logging for event operations
  - Custom `EventError` type

## Thread Safety

- Thread-safe event broadcasting
- Clone-able event bus instance
- Safe multi-subscriber support
- Atomic broadcast operations

## Performance Considerations

1. **Channel Capacity**
      - Configurable buffer size

2. **Concurrency**
      - Non-blocking operations
      - Multiple concurrent subscribers
      - Efficient event distribution

3. **Resource Management**
      - Automatic cleanup of dropped subscribers (via Tokio)
      - Pattern matching for event types

## Future Considerations

1. Event persistence options
2. Priority-based event handling
3. Event batching capabilities
4. Enhanced filtering mechanisms
5. Subscriber backpressure handling
6. Event replay functionality

---

*Version: 1.0*  
*Last Updated: 2025-08-05*  
*Component Owner: Steven Forrester*