# Crate for shared types for OpsML

## Structure
Each module corresponds to its use case in OpsML.

## Modules
- `api`: API types (route enums, request types)
- `cards`: Shared types for cards and registries
  - `data`: Data types for cards
  - `model`: Model types for cards
  - `run`: Run types for cards
- `contracts`: Shared types for server and client. These correspond to opsml_server routers
- `shared`: Shared generic types that are used throughout all crates