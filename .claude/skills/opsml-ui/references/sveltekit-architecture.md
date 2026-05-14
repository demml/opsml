# SvelteKit Architecture And BFF Patterns

## Table Of Contents

- Source files to inspect
- Route and load ownership
- BFF route handlers
- Data ownership and invalidation
- Error, auth, and session boundaries
- Anti-patterns
- Official references

## Source Files To Inspect

- `crates/opsml_server/opsml_ui/src/routes/+layout.server.ts`
- `crates/opsml_server/opsml_ui/src/routes/+layout.svelte`
- `crates/opsml_server/opsml_ui/src/routes/api/card/registry/page/+server.ts`
- `crates/opsml_server/opsml_ui/src/routes/api/scouter/observability/trace/+server.ts`
- `crates/opsml_server/opsml_ui/src/routes/opsml/agent/[registry]/card/[space]/[name]/[version]/observability/+page.ts`
- `crates/opsml_server/opsml_ui/src/lib/server/card/utils.ts`
- `crates/opsml_server/opsml_ui/src/lib/server/trace/utils.ts`

## Route And Load Ownership

- Use `+layout.server.ts` for app-wide server data such as UI settings, username, feature flags, and mock mode. Follow the root layout server pattern: catch backend failure, log it, and return a usable fallback.
- Use `+page.server.ts` when the page must access server-only state, cookies, credentials, or backend helpers that should not ship to the browser.
- Use universal `+page.ts` when the page needs browser-side reloads or SvelteKit `fetch` from the client, as observability does with `depends("trace:data")` and trace refreshes.
- Keep route data shaped for the UI. Do not pass raw backend responses through multiple components when a server load or BFF handler can normalize them once.
- SvelteKit load reruns update `data` without recreating components. Reset local component state only when the workflow requires it, using route keys or navigation hooks deliberately.

## BFF Route Handlers

Use `+server.ts` as a backend-for-frontend boundary when the UI needs aggregation, proxying, feature flags, mock fallback, or request shape cleanup.

Good OpsML patterns:

- `api/card/registry/page/+server.ts` accepts filter/sort/page/cursor input and delegates to `$lib/server/card/utils`.
- `api/scouter/observability/trace/+server.ts` reads filters, checks dev mock mode from cookies, calls server trace helpers, and returns a consistent `{ response, error }` envelope.
- Keep backend URL details, mock selection, and cross-service request quirks in `$lib/server/*` helpers or BFF route handlers.

Decision rules:

- Put secret-bearing or cookie-dependent logic on the server.
- Put fan-out aggregation on the server when it reduces client waterfalls or normalizes several backend calls into one UI payload.
- Keep client fetches for user-driven interactions such as loading the next trace page, applying filters, or refreshing a panel.
- Validate request shape at BFF boundaries when input is user-controlled or shared by multiple components.

## Data Ownership And Invalidation

- Use `depends("trace:data")` in load functions that need targeted invalidation.
- Use `invalidate("trace:data")` from client components when a retry, filter, or refresh should rerun the route load.
- Do not use broad invalidation when a local BFF call can update a small section of the page.
- Preserve URL state for shareable workflow state such as selected trace IDs, registry filters, or time ranges when users are likely to link or revisit the view.
- Store purely local UI state in components or `.svelte.ts` modules, not the URL.

## Error, Auth, And Session Boundaries

- Keep cookies and auth/session checks server-side unless the value is safe UI state.
- Return discriminated status shapes for pages that need rich error states: success, not found, disabled, unauthorized, failed.
- BFF endpoints should return structured errors that the UI can render without guessing.
- In page loads, distinguish empty data from backend failure. Empty trace results, Scouter disabled, and network errors need different UI states.
- Redirect only when navigation should change. For recoverable dashboard errors, render an in-page error with retry.

## Anti-Patterns

- Client components calling several backend endpoints sequentially on mount when a route load or BFF endpoint can aggregate.
- Fetching all rows to the browser for filtering or sorting.
- Exposing backend request schemas directly to deeply nested UI components.
- Putting cookies, tokens, or auth-sensitive logic in universal/client code.
- Calling `await parent()` before unrelated fetches when it creates a waterfall.
- Returning untyped loose objects that force component-level guessing.

## Official References

- SvelteKit load: https://svelte.dev/docs/kit/load
- SvelteKit app state: https://svelte.dev/docs/kit/$app-state
- SvelteKit routing: https://svelte.dev/docs/kit/routing
