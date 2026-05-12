---
name: opsml-ui
description: Broad skill for building, editing, debugging, styling, and extending the OpsML UI in `crates/opsml_server/opsml_ui`. Use for Svelte 5 components, SvelteKit routes/layouts/load functions, internal `/routes/api` proxy endpoints, UI stores, Tailwind or Skeleton styling, card pages, Scouter dashboards, observability or trace views, agent or prompt interfaces, and general frontend bugfix or feature work inside the embedded OpsML frontend.
---

Canonical skill for OpsML frontend work. The older `sveltekit-neobrutalism` skill is a legacy alias; use this skill as the source of truth for `crates/opsml_server/opsml_ui`.

Work inside the existing `opsml_ui` architecture and visual language rather than treating this as a generic Svelte app. OpsML is a dense developer tool, not a marketing site: build fast, scannable, task-oriented interfaces that expose operational details clearly.

Start by locating the feature boundary before editing:
- Read `references/working-map.md` to find the right feature area.

Then load only the topic references needed for the task:
- BFF/data-loading, server routes, load functions, invalidation, auth/session boundaries: read `references/sveltekit-architecture.md` and, for legacy route notes, `references/architecture.md`.
- Svelte component state, runes, snippets, effects, `.svelte.ts` modules, and legacy Svelte anti-patterns: read `references/svelte5-patterns.md` and, for shorter local patterns, `references/sveltekit-patterns.md`.
- Large tables, traces, files, charts, pagination, virtualization, search/filtering, and payload budgets: read `references/data-performance.md`.
- Developer workflow UX, registries, observability, trace inspection, filters, drilldowns, empty/loading/error states: read `references/developer-ux.md`.
- Tailwind v4, Skeleton, OpsML theme tokens, dark mode, icons, semantic color rules: read `references/theming.md` and, for short local rules, `references/design-system.md`.
- Vitest, Svelte Testing Library, pure utility tests, build/manual checks, accessibility and performance checks: read `references/testing-verification.md`.

Follow these repo-specific rules:
- Keep data fetching server-side by default. Prefer `+page.server.ts`, `+layout.server.ts`, and server helpers under `src/lib/server/`.
- Reuse the BFF shape already in the app. If a component needs backend access, prefer an internal SvelteKit `/routes/api/...` endpoint plus a server helper instead of calling the Rust backend directly from the browser.
- Reuse route constants from `src/lib/components/api/routes.ts` before introducing new path strings.
- Preserve OpsML theme tokens and brutalist interaction patterns. Do not introduce arbitrary hex colors, soft shadows, glassmorphism, or generic grayscale borders.
- Use `primary-*`, `secondary-*`, and `tertiary-*` for neutral UI categories. Reserve `success-*`, `warning-*`, and `error-*` for actual state, feedback, risk, or failure semantics.
- Keep types close to the feature unless they are clearly shared by multiple areas.
- Preserve the current auth flow in `src/hooks.server.ts` and `src/lib/server/auth/validateToken.ts`.
- Use `$derived(expression)` or `$derived.by(() => expression)` for derived state and keep derived values side-effect free.
- Use `$effect` mainly for external side effects such as browser APIs, observers, Chart.js, CodeMirror, imperative subscriptions, and request side effects.
- Prefer server-backed pagination, filtering, sorting, and aggregation for large remote datasets.
- Use `VirtualScroller.svelte` or `@tanstack/svelte-virtual` for large scrollable views.
- Do not add new UI libraries unless the user explicitly asks.

When making changes, inspect in this order:
1. The route entrypoint (`+page.svelte`, `+page.ts`, `+page.server.ts`, `+layout.*`)
2. The feature component under `src/lib/components/...`
3. The server helper under `src/lib/server/...`
4. Shared route constants, schema, or local feature types

Use these verification commands from `crates/opsml_server/opsml_ui` when relevant:
- `pnpm build`
- `pnpm exec svelte-check`
- `pnpm exec eslint .`

Prefer small, local edits that match existing patterns over broad refactors unless the task explicitly requires architectural cleanup.
