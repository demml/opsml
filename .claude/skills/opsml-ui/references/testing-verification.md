# Testing And Verification

## Table Of Contents

- Source files to inspect
- Choosing the test type
- Pure utility tests
- Component tests
- Route and load tests
- Manual UI checks
- Performance checks
- Verification commands

## Source Files To Inspect

- `crates/opsml_server/opsml_ui/package.json`
- `crates/opsml_server/opsml_ui/src/lib/components/utils/__tests__/CustomSelect.test.ts`
- `crates/opsml_server/opsml_ui/src/lib/components/trace/genai/__tests__/SpanGenAiPanel.test.ts`
- `crates/opsml_server/opsml_ui/src/routes/opsml/[registry]/card/[space]/[name]/[version]/observability/__tests__/page.test.ts`
- `crates/opsml_server/opsml_ui/src/lib/server/trace/facets.test.ts`
- `crates/opsml_server/opsml_ui/src/lib/components/files/utils.test.ts`

## Choosing The Test Type

- Use pure utility tests for data transforms, request builders, formatter behavior, trace/facet derivation, and schema validation.
- Use component tests for user-visible state changes, dropdown behavior, filter chips, tabs, copy buttons, and conditional panels.
- Use route/load tests when a page's status shape, mock mode behavior, registry guard, query param handling, or fallback logic changes.
- Use manual visual checks for dense layout, dark mode, responsive behavior, chart interactions, and large data performance.
- Do not require broad tests for small style-only changes unless the component is shared or dark-mode risky.

## Pure Utility Tests

Prefer moving complex logic out of Svelte components when it can be tested as TypeScript:

- trace facet derivation
- filter request building
- chart config builders
- file size and preview decisions
- date range calculations
- schema validation with zod

## Component Tests

Use Svelte Testing Library for component contracts:

- render expected labels and values
- call `onChange` once per user action
- show active filters immediately
- disable controls while loading
- keep empty and error states visible
- expose accessible labels for icon buttons

Mock heavyweight child components such as charts when the test is about parent behavior.

## Route And Load Tests

Route/load tests should assert shaped page states, not implementation details:

- success
- not found or empty
- service disabled
- mock mode
- backend error fallback
- query param selection, such as initial trace ID

Use local examples under route `__tests__` folders for mock `fetch`, `parent`, and fixture setup.

## Manual UI Checks

Before considering a meaningful UI change complete, inspect:

- light and dark mode
- narrow and desktop widths
- hover, focus, selected, disabled, empty, loading, and error states
- long names, long tags, long file paths, large payloads
- keyboard access for buttons, menus, dialogs, filters, and copy actions
- route navigation and back/forward behavior

For charts, verify tooltips, zoom/reset, theme colors, and empty series behavior.

## Performance Checks

For data-heavy views, test with enough volume to expose the design:

- many registry rows or versions
- trace pages with next and previous cursors
- spans with large attributes and events
- large code, JSON, and markdown files
- dashboard charts across long time ranges

Check for obvious re-render loops, scroll jumps, layout shift, unbounded DOM growth, stale responses after filter changes, and chart instances that are not destroyed.

## Verification Commands

From `crates/opsml_server/opsml_ui`:

- `pnpm test` - run Vitest.
- `pnpm build` - run the SvelteKit/Vite build.

From the repo root, use `git status --short` before finalizing to confirm the change set. For skill-only work, app tests are not required unless app code was touched.
