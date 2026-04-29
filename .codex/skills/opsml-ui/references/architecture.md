# OpsML UI Architecture

UI root: `crates/opsml_server/opsml_ui`

## Stack
- Svelte 5 with runes
- SvelteKit SSR routing
- Tailwind CSS v4
- Skeleton UI
- Embedded frontend served alongside the Rust backend

## Server/client split
- Route data should come from `+page.server.ts` or `+layout.server.ts` when possible.
- Shared backend-facing logic lives under `src/lib/server/`.
- Browser-facing BFF endpoints live under `src/routes/api/`.
- Avoid direct backend calls from browser components when an existing server helper or `/routes/api` proxy pattern fits.

## Core auth flow
- `src/hooks.server.ts` enforces auth for non-public routes and injects bearer tokens on server-side fetches.
- `src/lib/server/auth/validateToken.ts` and related server helpers own auth behavior.
- Treat cookies and token refresh as server concerns. Do not move auth handling into client components.

## Routing conventions
- Main product routes live under `src/routes/opsml/`.
- Internal API routes live under `src/routes/api/`.
- Dynamic card browsing is centered around:
  - `src/routes/opsml/[registry]/...`
  - `src/routes/opsml/[registry]/card/[space]/[name]/[version]/...`
- Agent-facing flows live under `src/routes/opsml/agent/...`.
- Observability and trace views live under `src/routes/opsml/observability/...`.

## API boundary conventions
- UI-visible path constants live in `src/lib/components/api/routes.ts`.
- Backend server client wrapper lives in `src/lib/server/api/opsmlClient.ts`.
- For new UI-to-backend calls:
  1. Add or reuse path constants
  2. Add a server helper in `src/lib/server/...`
  3. Add a `/routes/api/...` proxy if browser-side access is needed
  4. Keep feature types near the feature unless they are broadly reused

## State conventions
- Shared reactive stores use `.svelte.ts` files in feature or settings areas.
- Layout-level initialization currently happens in top-level layout loaders such as `src/routes/+layout.server.ts`.
- Prefer local rune state first; lift state only when multiple routes or components actually share it.

## File selection guide
- Need page behavior: inspect route files first
- Need reusable visual logic: inspect `src/lib/components/...`
- Need backend or data loading behavior: inspect `src/lib/server/...`
- Need routing or endpoint names: inspect `src/lib/components/api/routes.ts`
