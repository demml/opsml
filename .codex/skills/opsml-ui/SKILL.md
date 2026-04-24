---
name: opsml-ui
description: Broad skill for building, editing, debugging, styling, and extending the OpsML UI in `crates/opsml_server/opsml_ui`. Use for Svelte 5 components, SvelteKit routes/layouts/load functions, internal `/routes/api` proxy endpoints, UI stores, Tailwind or Skeleton styling, card pages, Scouter dashboards, observability or trace views, agent or prompt interfaces, and general frontend bugfix or feature work inside the embedded OpsML frontend.
---

Work inside the existing `opsml_ui` architecture and visual language rather than treating this as a generic Svelte app.

Start by locating the feature boundary before editing:
- Read `references/working-map.md` to find the right feature area.
- Read `references/architecture.md` when changing routes, `+page.server.ts`, `+layout.server.ts`, `hooks.server.ts`, or `/routes/api` proxies.
- Read `references/design-system.md` when changing styling, layout, tokens, component chrome, or dashboard presentation.
- Read `references/sveltekit-patterns.md` when changing TypeScript logic, runes, server loads, API typing, or reusable helpers.

Follow these repo-specific rules:
- Keep data fetching server-side by default. Prefer `+page.server.ts`, `+layout.server.ts`, and server helpers under `src/lib/server/`.
- Reuse the BFF shape already in the app. If a component needs backend access, prefer an internal SvelteKit `/routes/api/...` endpoint plus a server helper instead of calling the Rust backend directly from the browser.
- Reuse route constants from `src/lib/components/api/routes.ts` before introducing new path strings.
- Preserve OpsML theme tokens and brutalist interaction patterns. Do not introduce arbitrary hex colors, soft shadows, glassmorphism, or generic grayscale borders.
- Keep types close to the feature unless they are clearly shared by multiple areas.
- Preserve the current auth flow in `src/hooks.server.ts` and `src/lib/server/auth/validateToken.ts`.

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
