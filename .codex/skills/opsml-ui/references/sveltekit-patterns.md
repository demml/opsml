# OpsML SvelteKit and TypeScript Patterns

## TypeScript
- Assume strict TypeScript.
- Avoid `any`; use `unknown` and narrow at boundaries.
- Keep feature-local types near the feature.
- Reuse shared types only when multiple areas genuinely depend on them.

## Svelte 5 runes
- Use `$state` for local reactive state.
- Use `$derived` for pure computed values.
- Use `$effect` for side effects only.
- Keep derived logic pure and cheap.
- Do not move simple local UI state into shared stores unnecessarily.

## Data loading
- Prefer server-side loading in:
  - `+page.server.ts`
  - `+layout.server.ts`
- Use `+page.ts` only when the route truly needs client-side behavior for data shape or navigation handling.
- Keep API parsing and backend interaction in `src/lib/server/...` helpers rather than scattering fetch logic through components.

## Internal API proxies
- Browser-visible proxies belong in `src/routes/api/...`.
- Pair them with feature helpers in `src/lib/server/...`.
- Reuse `src/lib/components/api/routes.ts` for path constants.
- Avoid duplicating literal route strings across files.

## Client wrappers
- Backend-facing wrapper: `src/lib/server/api/opsmlClient.ts`
- Existing route constants: `src/lib/components/api/routes.ts`

## Component boundaries
- Route files own loading and composition.
- Components should receive prepared data and stay focused on presentation plus local interaction state.
- Shared helper logic should live in feature utilities before being promoted to a global utility.

## Practical editing order
When implementing a UI change:
1. Inspect the route entrypoint
2. Inspect the primary feature component
3. Inspect any server helper used by that route
4. Inspect path constants and local types

## Validation
Run the smallest useful check for the change:
- `pnpm build` for broad confidence
- `pnpm exec svelte-check` for Svelte and TS correctness
- `pnpm exec eslint .` for lint cleanup when touching multiple TS or Svelte files
