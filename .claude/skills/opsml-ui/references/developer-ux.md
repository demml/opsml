# Developer UX

## Table Of Contents

- Product posture
- Navigation and information hierarchy
- Registry and card views
- Observability and trace workflows
- Files and artifacts
- Filters and drilldowns
- Empty, loading, and error states
- Keyboard and copy workflows
- Anti-patterns

## Product Posture

OpsML is a workbench for technical users. The UI should help users answer concrete questions:

- What exists?
- What changed?
- What failed?
- Where did this model, data card, prompt, service, trace, or alert come from?
- What should I inspect or do next?

Prioritize scan speed, stable layout, and clear operational metadata over decorative composition.

## Navigation And Information Hierarchy

- Preserve the existing app shell and Sidebar route model.
- Keep major resources under predictable groups: spaces, models, data, agents, experiments, services, observability.
- Use tabs for sibling views of the same entity, not unrelated workflows.
- Prefer split panes or side drawers for inspect-and-return workflows such as trace details and file previews.
- Keep breadcrumbs, entity names, versions, spaces, registry type, and status visible near the top of detail views.

## Registry And Card Views

- Registry pages should favor searchable, filterable lists with compact metadata.
- Show identity fields first: space, name, version, UID, registry type.
- Keep actions predictable: open, copy UID/path, favorite, compare, view files, view monitoring.
- Use status badges for functional state, not decoration.
- Make version navigation efficient. Users should not lose context when paging through versions.

## Observability And Trace Workflows

- Observability views should answer: volume, latency, errors, cost/tokens, service/model, and time range.
- Put filters close to results: time range, service, namespace, version, status, operation, model, tags.
- Keep selected trace detail adjacent to the trace list. Avoid full-page navigation for every trace inspection unless a shareable URL is required.
- In trace details, prioritize waterfall timing, status/error, model/tool calls, input/output previews, attributes, events, and resource metadata.
- Use lazy panels for verbose payloads and nested span details.
- Always provide a route or query param for shareable trace context when the workflow benefits from collaboration.

## Files And Artifacts

- Use a file tree plus detail pane for repository-like browsing.
- Show file size and type before rendering expensive content.
- Preview large files and require an explicit action for full content.
- Provide copy actions for paths, identifiers, JSON fragments, code snippets, and URLs.
- Keep binary/image/file-not-supported states direct and actionable.

## Filters And Drilldowns

- Active filters should be visible as removable chips or a compact summary.
- Filter changes should have immediate UI feedback and predictable refetch behavior.
- Expensive filters should be server-backed and debounced.
- Facets should reflect the current time range and resource context.
- Drilldowns should preserve the parent context, usually with a side panel, nested route, or query param.

## Empty, Loading, And Error States

- Empty states should name the current scope and suggest the next useful adjustment.
- Loading states should preserve panel dimensions and avoid reflow.
- Error states should distinguish:
  - no data
  - service disabled
  - unauthorized
  - network/backend failure
  - malformed response
- Retry actions should invalidate or refetch the smallest useful scope.
- Do not hide partial data because one secondary request failed. Render available data and show a localized warning.

## Keyboard And Copy Workflows

- Use real buttons and links so keyboard navigation works without extra ARIA.
- Give icon-only buttons an accessible label.
- Keep focus visible against both light and dark themes.
- Provide copy actions for technical identifiers users need in issues, logs, or terminals.
- Preserve selection after refresh when possible.

## Anti-Patterns

- Marketing-style hero sections for operational tools.
- Big decorative cards that push data below the fold.
- Modal-only workflows for routine inspection.
- Hiding errors behind generic "something went wrong" copy.
- Tables with unstable row height, shifting columns, or unbounded cells.
- Requiring users to navigate away just to inspect a payload, span, or file.
