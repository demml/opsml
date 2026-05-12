# Data Performance

## Table Of Contents

- Source files to inspect
- Decision rules
- Pagination and filtering
- Virtualization
- Search and derived state
- Charts
- Files, code, and markdown
- Request cancellation and budgets
- Anti-patterns
- Official references

## Source Files To Inspect

- `crates/opsml_server/opsml_ui/src/lib/components/utils/VirtualScroller.svelte`
- `crates/opsml_server/opsml_ui/src/lib/components/trace/TraceInfiniteScroll.svelte`
- `crates/opsml_server/opsml_ui/src/lib/components/trace/TraceTable.svelte`
- `crates/opsml_server/opsml_ui/src/lib/components/trace/MetricChart.svelte`
- `crates/opsml_server/opsml_ui/src/lib/components/files/CodeViewer.svelte`
- `crates/opsml_server/opsml_ui/src/lib/components/files/fileSizeManager.svelte.ts`
- `crates/opsml_server/opsml_ui/src/routes/api/card/registry/page/+server.ts`
- `crates/opsml_server/opsml_ui/src/routes/api/scouter/observability/trace/+server.ts`

## Decision Rules

- If a dataset is remote and can grow beyond one screen, assume server-backed pagination, filtering, and sorting.
- If a list renders more than a few hundred rows, use virtualization or pagination before adding richer cells.
- If a row opens heavy detail, lazy-load the detail panel rather than attaching all nested content to every row.
- If a chart has more points than pixels, aggregate or downsample server-side or in a utility before rendering.
- If content can be very large, show a preview and require explicit user action for full content.

## Pagination And Filtering

- Prefer cursor or keyset pagination for trace streams, logs, events, and registry pages where ordering matters.
- Keep page sizes modest. OpsML trace flows commonly use limits around 50 and retain a bounded client window.
- Send search terms, filters, tags, sort fields, time ranges, and cursor values to BFF endpoints.
- Return enough cursor metadata for next and previous navigation.
- Keep empty result states distinct from backend failure.
- Do not fetch all registry cards, traces, spans, alerts, or files only to filter in Svelte.

## Virtualization

- Use `VirtualScroller.svelte` for fixed-height rows and bidirectional infinite scroll.
- Use `@tanstack/svelte-virtual` when variable list behavior or library ergonomics fit better than the local scroller.
- Provide stable keys such as `trace_id`, `uid`, or a composite key.
- Keep row height stable. Expand details in a side panel or below a selected row, not inside every virtualized row.
- Use overscan intentionally. Too little causes blanking; too much defeats virtualization.
- Preserve scroll anchors when prepending data, as `VirtualScroller.svelte` does.

## Search And Derived State

- Debounce user text input when it triggers network requests or expensive transforms.
- For small local lists, a derived search/sort is fine.
- For large arrays, avoid recreating full sorted and filtered copies on every keystroke. Move the operation server-side or into a bounded derived view model.
- Keep filter chips and active filter state typed so the request payload is stable.
- Avoid template-level calls to expensive formatting for every cell. Precompute row view models for dense tables.

## Charts

- Use existing Chart.js wrappers and chart utility builders.
- Destroy Chart.js instances on component teardown and before recreation.
- Recreate or update charts when theme tokens change.
- Use backend bucket intervals that match the selected time range.
- Prefer aggregated series for dashboards: counts, latency percentiles, error rates, cost, tokens, or drift summaries.
- Keep zoom/reset controls visible and keyboard reachable.

## Files, Code, And Markdown

- Follow `CodeViewer.svelte`: preview large files, disable expensive highlighting for very large content, and use bounded scroll containers.
- Do not render huge markdown or code blobs unbounded in the page.
- For tree views, lazy-load folders or file contents when selected.
- For JSON, avoid formatting very large payloads on every render. Format once or preview first.

## Request Cancellation And Budgets

- Cancel stale requests when users rapidly change filters, time ranges, or search text.
- Ignore out-of-order responses using a request id when cancellation is not available.
- Establish budgets before implementing:
  - initial payload count and approximate byte size
  - max client-retained rows
  - row height and expected visible row count
  - chart point count per series
  - acceptable refetch frequency
- Use loading states that preserve layout size, especially in dashboards and tables.

## Anti-Patterns

- Client-side filtering of unbounded trace or registry datasets.
- Rendering all spans, events, attributes, and payloads for every trace row.
- Rebuilding charts without destroying old instances.
- Formatting large JSON or markdown in markup.
- Infinite scroll without a max retained item window.
- Fetching facets, metrics, rows, and details sequentially when they can be parallel or server-aggregated.

## Official References

- SvelteKit performance: https://svelte.dev/docs/kit/performance
- SvelteKit load: https://svelte.dev/docs/kit/load
