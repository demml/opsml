# Svelte 5 Patterns

## Table Of Contents

- Source files to inspect
- Runes
- Props, snippets, and callbacks
- Effects and lifecycle
- Shared state
- Anti-patterns
- Official references

## Source Files To Inspect

- `crates/opsml_server/opsml_ui/src/lib/components/utils/VirtualScroller.svelte`
- `crates/opsml_server/opsml_ui/src/lib/components/nav/Sidebar.svelte`
- `crates/opsml_server/opsml_ui/src/lib/components/settings/theme.svelte.ts`
- `crates/opsml_server/opsml_ui/src/lib/components/files/CodeViewer.svelte`
- `crates/opsml_server/opsml_ui/src/lib/components/trace/MetricChart.svelte`

## Runes

- Use `$state` for local mutable component state.
- Use `$derived(expression)` for simple values that can be computed from current state and props.
- Use `$derived.by(() => expression)` when the derivation needs branching or several statements.
- Read derived values directly in script and markup.
- Keep derived state pure. Derivations should not fetch, mutate unrelated state, subscribe, or touch the DOM.
- Use stable keys in `{#each}` blocks for rows, traces, cards, and filter chips.

Example:

```svelte
<script lang="ts">
  let selectedId = $state<string | null>(null);

  const selected = $derived(
    rows.find((row) => row.id === selectedId) ?? null
  );

  const sortedRows = $derived.by(() => {
    const copy = rows.slice();
    copy.sort((a, b) => a.name.localeCompare(b.name));
    return copy;
  });
</script>

{#each sortedRows as row (row.id)}
  <button type="button" onclick={() => (selectedId = row.id)}>
    {row.name}
  </button>
{/each}
```

## Props, Snippets, And Callbacks

- Type props with a local `type Props` or interface when the prop shape is non-trivial.
- Use callback props for parent-owned state, for example `onSelect`, `onChange`, `onRefresh`.
- Do not mutate props directly. Ask the parent to update state.
- Use snippets for repeated cell/detail rendering, as `VirtualScroller.svelte` does with `children`.
- Prefer semantic elements with `type="button"` over clickable `div` wrappers.

## Effects And Lifecycle

- Use `onMount` for browser-only APIs: DOM measurement, observers, local storage setup, media query listeners, and client-only initialization.
- Use `$effect` for external side effects: Chart.js lifecycle, CodeMirror setup, request side effects, imperative subscriptions, or syncing with browser APIs.
- Return cleanup functions for observers, event listeners, and third-party instances.
- Avoid using effects to copy derived values into state.
- When an effect fetches, guard stale responses with cancellation, a request token, or `AbortController`.

OpsML examples:

- `MetricChart.svelte` uses effects to reset zoom and recreate Chart.js instances when config or theme changes.
- `theme.svelte.ts` gates browser-only local storage and media query behavior with `browser`.
- `VirtualScroller.svelte` uses `onMount` and `ResizeObserver` for container measurement.

## Shared State

- Use `.svelte.ts` modules for small, cohesive client-side state such as theme, time range, or UI preferences.
- Keep shared state APIs narrow: getters plus purposeful actions.
- Do not make a global store for page-specific state that should reset on route changes.
- Persist only state users expect to survive navigation.

## Anti-Patterns

- Legacy reactive labels for new code.
- Legacy event directives in new code.
- Broad untyped prop bags.
- Large components that mix fetch orchestration, filtering, chart setup, modal state, and rendering.
- Effects that exist only to keep two pieces of local state in sync.
- DOM querying when `bind:this` or component state is enough.

## Official References

- Svelte derived state: https://svelte.dev/docs/svelte/$derived
- Svelte effects: https://svelte.dev/docs/svelte/$effect
- Svelte props: https://svelte.dev/docs/svelte/$props
- Svelte snippets: https://svelte.dev/docs/svelte/snippet
