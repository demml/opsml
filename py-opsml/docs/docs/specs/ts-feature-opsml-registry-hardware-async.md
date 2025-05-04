# Technical Changes: OpsmlRegistry Async/Sync Handling

## Overview
Implementation of proper async/sync handling in `OpsmlRegistry` with specific focus on hardware metrics collection and background task management.

## Key Changes

### 1. Hardware Metrics Insertion
```rust
pub async fn insert_hardware_metrics(&self, metrics: HardwareMetricRequest) -> Result<(), RegistryError>
```
- Implemented async hardware metrics insertion
- Uses `spawn_blocking` for client-side operations to prevent runtime blocking
- Maintains pure async flow for server-side operations
- Properly handles ownership and lifetime issues through cloning

### 2. Registry Mode Handling
- **Client Mode**: 
  - Uses blocking operations wrapped in `spawn_blocking`
  - Clones registry instances to avoid lifetime issues
  - Integrates with `app_state().runtime` for task management

- **Server Mode**:
  - Pure async implementation
  - Direct awaiting of server operations
  - No blocking operations required

## Implementation Details

### Client Registry Pattern
```rust
Self::ClientRegistry(client_registry) => {
    let client_registry = client_registry.clone();
    app_state()
        .runtime
        .spawn_blocking(move || client_registry.insert_hardware_metrics(&metrics))
        .await
}
```

### Server Registry Pattern
```rust
Self::ServerRegistry(server_registry) => {
    server_registry.insert_hardware_metrics(&metrics).await
}
```

## Benefits
1. Prevents runtime panics from mixing async/sync contexts
2. Maintains consistent performance characteristics
3. Properly handles both client and server modes
4. Uses shared application state runtime
5. Clean separation of concerns between client and server implementations

## Breaking Changes
None - Implementation maintains backward compatibility while improving internal handling.

## Dependencies
- Requires `app_state()` runtime
- Relies on `tokio` for async runtime
- Uses existing error handling through `RegistryError`

---

*Version: 3.0*  
*Last Updated: 2025-04-02*  
*Component Owner: Steven Forrester*