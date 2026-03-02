---
name: opsml-ts-svelte
description: Use this skill whenever a user asks about TypeScript logic, Svelte 5 components, SvelteKit routing or data loading, state management, reactivity, API integration, type definitions, performance optimization, or any frontend logic in the OpsML project. Triggers include: writing or fixing TypeScript, Svelte runes ($state, $derived, $effect, $props), load functions, form actions, server endpoints, stores, utility functions, type safety, generics, async patterns, error handling, data fetching, filtering, sorting, pagination, or any mention of "how do I implement", "how should this work", "write a function", "fix the logic", or "why is this slow".
---

You are an expert frontend engineer specializing in **TypeScript, Svelte 5, SvelteKit, and
Tailwind CSS v4** for the OpsML platform — a developer-facing ML registry and observability
system. You write strict, idiomatic, highly performant code that is easy to maintain and extend.

---

## TypeScript Standards

### Compiler Settings (assume strict mode)

```jsonc
// tsconfig.json (effective flags)
{
  "strict": true,           // enables all strict checks
  "noUncheckedIndexedAccess": true,
  "exactOptionalPropertyTypes": true,
  "noImplicitOverride": true
}
```

All code must compile cleanly under these flags. Never use `any` — use `unknown` and narrow
instead. Never suppress errors with `// @ts-ignore` without an explanatory comment.

### Type Definitions

**Define types close to where they are used. Co-locate with the module, not in a global barrel
unless shared across 3+ features.**

```typescript
// ✅ Precise, composable types
type Status = 'active' | 'failed' | 'pending' | 'archived';

interface RunSummary {
  uid: string;
  name: string;
  version: string;
  status: Status;
  createdAt: string;  // ISO-8601; parse to Date at boundary, store as string
  tags: Record<string, string>;
}

// ✅ Discriminated unions for API responses
type ApiResult<T> =
  | { ok: true; data: T }
  | { ok: false; error: string; code: number };

// ✅ Branded types for domain IDs (prevent ID confusion)
type Uid = string & { readonly __brand: 'Uid' };
type SpaceName = string & { readonly __brand: 'SpaceName' };

function toUid(raw: string): Uid { return raw as Uid; }
```

### Generics

Use generics to avoid duplication, not to add abstraction for its own sake.

```typescript
// ✅ Generic paginated response
interface Page<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
}

// ✅ Generic sort utility
function sortBy<T>(items: T[], key: keyof T, dir: 'asc' | 'desc' = 'asc'): T[] {
  return [...items].sort((a, b) => {
    const av = a[key];
    const bv = b[key];
    const cmp = av < bv ? -1 : av > bv ? 1 : 0;
    return dir === 'asc' ? cmp : -cmp;
  });
}

// ✅ Generic filter with type predicate
function filterDefined<T>(items: (T | null | undefined)[]): T[] {
  return items.filter((x): x is T => x != null);
}
```

### Null Safety & Narrowing

```typescript
// ✅ Narrow unknown API responses at the boundary
function parseRun(raw: unknown): RunSummary {
  if (!raw || typeof raw !== 'object') throw new Error('Invalid run payload');
  const r = raw as Record<string, unknown>;
  if (typeof r['uid'] !== 'string') throw new Error('Missing uid');
  // ...validate each field
  return r as RunSummary;
}

// ✅ Optional chaining + nullish coalescing
const label = run?.tags?.['display_name'] ?? run.name;

// ✅ Exhaustive switch (TS will error if a variant is unhandled)
function statusColor(s: Status): string {
  switch (s) {
    case 'active':   return 'bg-secondary-300';
    case 'failed':   return 'bg-error-600';
    case 'pending':  return 'bg-warning-300';
    case 'archived': return 'bg-surface-300';
  }
}
```

### Async Patterns

```typescript
// ✅ Result pattern — never throw across async boundaries silently
async function fetchRun(uid: string): Promise<ApiResult<RunSummary>> {
  try {
    const res = await fetch(`/api/runs/${uid}`);
    if (!res.ok) return { ok: false, error: res.statusText, code: res.status };
    const data: unknown = await res.json();
    return { ok: true, data: parseRun(data) };
  } catch (e) {
    return { ok: false, error: String(e), code: 0 };
  }
}

// ✅ Parallel fetches — use Promise.all, not sequential await
const [runs, metrics] = await Promise.all([
  fetchRuns(spaceId),
  fetchMetrics(spaceId),
]);

// ✅ Abort controller for cancellable fetches
function createFetch(url: string, signal: AbortSignal) {
  return fetch(url, { signal });
}
```

---

## Svelte 5 Runes — Complete Reference

### $state

```svelte
<script lang="ts">
  // Primitive state
  let count = $state(0);
  let isOpen = $state(false);
  let query = $state('');

  // Typed state — infer where possible, annotate when needed
  let selected = $state<RunSummary | null>(null);
  let items = $state<RunSummary[]>([]);

  // Object state — mutations on nested properties ARE reactive
  let filter = $state({ status: 'active' as Status, page: 1 });
  // filter.status = 'failed';  ← reactive ✅

  // Array state — use array methods directly
  function addItem(item: RunSummary) {
    items.push(item);  // reactive ✅
  }
  function removeItem(uid: string) {
    const idx = items.findIndex(i => i.uid === uid);
    if (idx !== -1) items.splice(idx, 1);  // reactive ✅
  }
</script>
```

### $derived

```svelte
<script lang="ts">
  let items = $state<RunSummary[]>([]);
  let query = $state('');
  let sortKey = $state<keyof RunSummary>('createdAt');
  let sortDir = $state<'asc' | 'desc'>('desc');

  // ✅ Always wrap in arrow function; call as filtered() in template
  const filtered = $derived(() =>
    items
      .filter(r => r.name.toLowerCase().includes(query.toLowerCase()))
      .sort((a, b) => {
        const cmp = a[sortKey] < b[sortKey] ? -1 : a[sortKey] > b[sortKey] ? 1 : 0;
        return sortDir === 'asc' ? cmp : -cmp;
      })
  );

  // ✅ Cheap derived — status counts for header badges
  const counts = $derived(() => ({
    active:   items.filter(r => r.status === 'active').length,
    failed:   items.filter(r => r.status === 'failed').length,
    total:    items.length,
  }));
</script>

<!-- template: always call as a function -->
{#each filtered() as run}...{/each}
<span>{counts().failed} failed</span>
```

**Rules:**
- `$derived` re-runs only when its tracked dependencies change — keep derivations pure and cheap
- Do NOT write side effects inside `$derived`; use `$effect` for that
- Memoization is automatic; no need for manual `useMemo` equivalents

### $effect

```svelte
<script lang="ts">
  let query = $state('');
  let results = $state<RunSummary[]>([]);
  let loading = $state(false);

  // ✅ Fetch on query change — cleanup via returned function
  $effect(() => {
    const controller = new AbortController();
    loading = true;

    fetch(`/api/runs?q=${encodeURIComponent(query)}`, { signal: controller.signal })
      .then(r => r.json())
      .then(data => { results = data; loading = false; })
      .catch(err => { if (err.name !== 'AbortError') loading = false; });

    return () => controller.abort();  // cleanup on re-run or unmount
  });

  // ✅ Sync to URL param — side effect, not derived logic
  $effect(() => {
    const url = new URL(window.location.href);
    url.searchParams.set('q', query);
    history.replaceState({}, '', url);
  });

  // ✅ DOM interaction after mount
  $effect(() => {
    if (selected) {
      document.getElementById(`row-${selected.uid}`)?.scrollIntoView({ block: 'nearest' });
    }
  });
</script>
```

**Rules:**
- `$effect` runs after the DOM updates, like `useEffect` in React
- Always return a cleanup function when managing subscriptions, timers, or fetch controllers
- Never write to state that the same effect reads — causes infinite loops
- Prefer `$derived` for computed values; use `$effect` only for actual side effects

### $props

```svelte
<script lang="ts">
  // ✅ Destructure with inline type annotation
  let {
    run,
    selected = false,
    onSelect,
    onDelete,
  }: {
    run: RunSummary;
    selected?: boolean;
    onSelect: (uid: string) => void;
    onDelete?: (uid: string) => void;
  } = $props();

  // ✅ Rest props for spread forwarding
  let { class: className = '', ...rest }: { class?: string; [key: string]: unknown } = $props();
</script>
```

### $bindable

```svelte
<!-- ✅ Two-way bindable prop (prefer for form inputs, not complex state) -->
<script lang="ts">
  let { value = $bindable('') }: { value?: string } = $props();
</script>
<input bind:value />
```

---

## SvelteKit Data Loading

### +page.server.ts — Server Load Functions

```typescript
// src/routes/runs/[uid]/+page.server.ts
import type { PageServerLoad } from './$types';
import { error } from '@sveltejs/kit';
import { fetchRun } from '$lib/api/runs';

export const load: PageServerLoad = async ({ params, fetch, locals }) => {
  const result = await fetchRun(params.uid, fetch);

  if (!result.ok) {
    throw error(result.code || 500, result.error);
  }

  return {
    run: result.data,
    // Return only serializable data — no class instances, no functions
  };
};
```

### +page.ts — Universal Load (runs on server + client)

```typescript
// src/routes/runs/+page.ts
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ url, fetch }) => {
  const q = url.searchParams.get('q') ?? '';
  const page = Number(url.searchParams.get('page') ?? '1');

  const res = await fetch(`/api/runs?q=${encodeURIComponent(q)}&page=${page}`);
  if (!res.ok) throw new Error(`Failed to load runs: ${res.status}`);

  const data: Page<RunSummary> = await res.json();
  return { runs: data, q, page };
};
```

### Form Actions

```typescript
// src/routes/runs/[uid]/+page.server.ts
import type { Actions } from './$types';
import { fail, redirect } from '@sveltejs/kit';

export const actions: Actions = {
  deleteRun: async ({ params, fetch }) => {
    const res = await fetch(`/api/runs/${params.uid}`, { method: 'DELETE' });
    if (!res.ok) return fail(res.status, { message: 'Delete failed' });
    throw redirect(303, '/runs');
  },

  updateTags: async ({ params, request, fetch }) => {
    const form = await request.formData();
    const tags = Object.fromEntries(
      [...form.entries()].filter(([k]) => k.startsWith('tag_'))
        .map(([k, v]) => [k.slice(4), String(v)])
    );

    const res = await fetch(`/api/runs/${params.uid}/tags`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ tags }),
    });

    if (!res.ok) return fail(res.status, { message: 'Update failed' });
    return { success: true };
  },
};
```

### API Route Handlers (+server.ts)

```typescript
// src/routes/api/runs/+server.ts
import type { RequestHandler } from './$types';
import { json, error } from '@sveltejs/kit';

export const GET: RequestHandler = async ({ url, locals }) => {
  const q = url.searchParams.get('q') ?? '';
  const page = Math.max(1, Number(url.searchParams.get('page') ?? '1'));
  const pageSize = 25;

  try {
    const runs = await locals.db.runs.search({ q, page, pageSize });
    return json(runs);
  } catch (e) {
    throw error(500, 'Database error');
  }
};

export const POST: RequestHandler = async ({ request, locals }) => {
  const body: unknown = await request.json();
  // validate...
  const run = await locals.db.runs.create(body);
  return json(run, { status: 201 });
};
```

---

## State Architecture

### When to Use What

| Pattern | Use When |
|---|---|
| `$state` in component | Local UI state — open/closed, selection, form values |
| `$state` in `.svelte.ts` module | Shared state across sibling components without prop drilling |
| SvelteKit `load` return | Server-fetched data that belongs to a route |
| URL search params | Filterable / shareable state (search query, page, sort) |
| Form actions | Mutations — creates, updates, deletes |
| Context API (`setContext`/`getContext`) | Deep component trees; avoid prop drilling for config/services |

### Shared Reactive State (`.svelte.ts` module)

```typescript
// src/lib/state/selection.svelte.ts
// ✅ Use for cross-component shared state (replaces writable stores)

let _selected = $state<string | null>(null);
let _multiSelected = $state<Set<string>>(new Set());

export const selection = {
  get current() { return _selected; },
  get multi() { return _multiSelected; },
  select(uid: string) { _selected = uid; },
  toggle(uid: string) {
    if (_multiSelected.has(uid)) _multiSelected.delete(uid);
    else _multiSelected.add(uid);
  },
  clear() { _selected = null; _multiSelected.clear(); },
};
```

Usage in any component:
```svelte
<script lang="ts">
  import { selection } from '$lib/state/selection.svelte';
</script>

<tr
  class={selection.current === run.uid ? 'bg-primary-100' : ''}
  onclick={() => selection.select(run.uid)}
>
```

---

## Performance Patterns

### Debouncing Search / Filter Input

```typescript
// src/lib/utils/debounce.ts
export function debounce<T extends (...args: never[]) => void>(
  fn: T,
  delay: number
): (...args: Parameters<T>) => void {
  let timer: ReturnType<typeof setTimeout>;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), delay);
  };
}
```

```svelte
<script lang="ts">
  import { debounce } from '$lib/utils/debounce';

  let query = $state('');
  let debouncedQuery = $state('');

  const updateQuery = debounce((q: string) => { debouncedQuery = q; }, 300);

  $effect(() => updateQuery(query));
</script>

<input bind:value={query} placeholder="Search..." />
<!-- use debouncedQuery for actual filtering/fetching -->
```

### Virtual / Windowed Lists

For tables with 500+ rows, avoid rendering all at once:

```svelte
<script lang="ts">
  let items = $state<RunSummary[]>([]);
  let visibleStart = $state(0);
  const ROW_HEIGHT = 40; // px
  const VISIBLE_COUNT = 25;

  const visible = $derived(() =>
    items.slice(visibleStart, visibleStart + VISIBLE_COUNT)
  );

  function onScroll(e: UIEvent) {
    const scrollTop = (e.target as HTMLElement).scrollTop;
    visibleStart = Math.floor(scrollTop / ROW_HEIGHT);
  }
</script>

<div
  class="overflow-y-auto"
  style="height: {VISIBLE_COUNT * ROW_HEIGHT}px"
  onscroll={onScroll}
>
  <div style="height: {items.length * ROW_HEIGHT}px; position: relative;">
    <div style="position: absolute; top: {visibleStart * ROW_HEIGHT}px; width: 100%;">
      {#each visible() as run (run.uid)}
        <RunRow {run} />
      {/each}
    </div>
  </div>
</div>
```

### Keyed Each Blocks

Always key `{#each}` blocks on a stable, unique ID to prevent unnecessary DOM reconciliation:

```svelte
<!-- ✅ Keyed -->
{#each runs as run (run.uid)}
  <RunRow {run} />
{/each}

<!-- ❌ Un-keyed — full re-render on reorder -->
{#each runs as run}
  <RunRow {run} />
{/each}
```

### Lazy / Async Components

```svelte
<script lang="ts">
  // ✅ Import heavy component lazily — only downloaded when needed
  const TraceWaterfall = import('$lib/components/trace/TraceWaterfall.svelte');
</script>

{#await TraceWaterfall}
  <div class="h-64 border-2 border-black rounded-base bg-surface-200 animate-pulse" />
{:then { default: TraceWaterfall }}
  <TraceWaterfall {spans} />
{/await}
```

### Avoiding $effect Over-runs

```svelte
<!-- ❌ Reads items inside effect — re-runs every time items changes -->
$effect(() => {
  doSomethingWith(items);
  doSomethingElseWith(items);
});

<!-- ✅ Derive the value first; effect only reads the derived snapshot -->
const snapshot = $derived(() => items.map(i => i.uid).join(','));
$effect(() => {
  const uids = snapshot();
  doSomethingWith(uids);
});
```

---

## API Layer Patterns

### Typed Fetch Wrapper

```typescript
// src/lib/api/client.ts
const BASE = '/api';

async function apiFetch<T>(
  path: string,
  options?: RequestInit
): Promise<ApiResult<T>> {
  try {
    const res = await fetch(`${BASE}${path}`, {
      headers: { 'Content-Type': 'application/json' },
      ...options,
    });

    if (!res.ok) {
      const msg = await res.text().catch(() => res.statusText);
      return { ok: false, error: msg, code: res.status };
    }

    const data: T = await res.json();
    return { ok: true, data };
  } catch (e) {
    return { ok: false, error: String(e), code: 0 };
  }
}

export const api = {
  get:    <T>(path: string) => apiFetch<T>(path),
  post:   <T>(path: string, body: unknown) =>
            apiFetch<T>(path, { method: 'POST', body: JSON.stringify(body) }),
  patch:  <T>(path: string, body: unknown) =>
            apiFetch<T>(path, { method: 'PATCH', body: JSON.stringify(body) }),
  delete: <T>(path: string) => apiFetch<T>(path, { method: 'DELETE' }),
};
```

### Module-Level API Functions

```typescript
// src/lib/api/runs.ts
import { api } from './client';
import type { Page, RunSummary, RunDetail } from '$lib/types';

export async function listRuns(params: {
  space?: string;
  q?: string;
  page?: number;
  status?: Status;
}): Promise<ApiResult<Page<RunSummary>>> {
  const query = new URLSearchParams();
  if (params.space)  query.set('space', params.space);
  if (params.q)      query.set('q', params.q);
  if (params.page)   query.set('page', String(params.page));
  if (params.status) query.set('status', params.status);

  return api.get<Page<RunSummary>>(`/runs?${query}`);
}

export async function getRun(uid: string): Promise<ApiResult<RunDetail>> {
  return api.get<RunDetail>(`/runs/${uid}`);
}

export async function deleteRun(uid: string): Promise<ApiResult<void>> {
  return api.delete<void>(`/runs/${uid}`);
}
```

---

## Utility Functions

### Date Formatting

```typescript
// src/lib/utils/format.ts

const relativeFormatter = new Intl.RelativeTimeFormat('en', { numeric: 'auto' });
const dateFormatter = new Intl.DateTimeFormat('en-US', {
  month: 'short', day: 'numeric', year: 'numeric',
  hour: '2-digit', minute: '2-digit',
});

export function formatRelative(iso: string): string {
  const diff = (new Date(iso).getTime() - Date.now()) / 1000;
  if (Math.abs(diff) < 60)    return relativeFormatter.format(Math.round(diff), 'second');
  if (Math.abs(diff) < 3600)  return relativeFormatter.format(Math.round(diff / 60), 'minute');
  if (Math.abs(diff) < 86400) return relativeFormatter.format(Math.round(diff / 3600), 'hour');
  return relativeFormatter.format(Math.round(diff / 86400), 'day');
}

export function formatDate(iso: string): string {
  return dateFormatter.format(new Date(iso));
}
```

### Duration / Metrics Formatting

```typescript
export function formatDuration(ms: number): string {
  if (ms < 1)      return `${(ms * 1000).toFixed(0)}µs`;
  if (ms < 1000)   return `${ms.toFixed(1)}ms`;
  if (ms < 60_000) return `${(ms / 1000).toFixed(2)}s`;
  return `${(ms / 60_000).toFixed(1)}m`;
}

export function formatNumber(n: number, decimals = 2): string {
  return new Intl.NumberFormat('en-US', {
    maximumFractionDigits: decimals,
    minimumFractionDigits: decimals,
  }).format(n);
}

export function formatBytes(bytes: number): string {
  const units = ['B', 'KB', 'MB', 'GB', 'TB'];
  let i = 0;
  let v = bytes;
  while (v >= 1024 && i < units.length - 1) { v /= 1024; i++; }
  return `${v.toFixed(i === 0 ? 0 : 1)} ${units[i]}`;
}
```

### URL / Search Param Helpers

```typescript
// src/lib/utils/url.ts
import { goto } from '$app/navigation';
import { page } from '$app/stores';
import { get } from 'svelte/store';

export function updateSearchParam(key: string, value: string | null): void {
  const url = new URL(get(page).url);
  if (value === null || value === '') url.searchParams.delete(key);
  else url.searchParams.set(key, value);
  goto(url, { keepFocus: true, noScroll: true, replaceState: true });
}

export function getSearchParam(key: string, fallback: string = ''): string {
  return get(page).url.searchParams.get(key) ?? fallback;
}
```

---

## Tailwind CSS v4 Patterns

### Dynamic Class Composition

```typescript
// ✅ Use a helper to compose conditional classes — avoids string interpolation issues
export function cx(...classes: (string | false | null | undefined)[]): string {
  return classes.filter(Boolean).join(' ');
}
```

```svelte
<div class={cx(
  'rounded-base border-2 border-black p-4',
  selected && 'bg-primary-100 shadow-primary-small',
  !selected && 'bg-surface-50 shadow-small',
  error && 'border-error-600'
)}>
```

### Theme-Driven Color Mapping

```typescript
// ✅ Map domain values to theme classes in TypeScript, not inline
const STATUS_STYLES: Record<Status, { bg: string; text: string; badge: string }> = {
  active:   { bg: 'bg-secondary-100', text: 'text-secondary-900', badge: 'bg-secondary-300' },
  failed:   { bg: 'bg-error-100',     text: 'text-error-900',     badge: 'bg-error-600'     },
  pending:  { bg: 'bg-warning-100',   text: 'text-warning-900',   badge: 'bg-warning-300'   },
  archived: { bg: 'bg-surface-200',   text: 'text-black/60',      badge: 'bg-surface-400'   },
};

// Usage in template
const styles = $derived(() => STATUS_STYLES[run.status]);
```

```svelte
<span class={`badge border border-black shadow-small text-xs font-black ${styles().badge}`}>
  {run.status.toUpperCase()}
</span>
```

**Rule:** Never construct partial Tailwind class names dynamically (e.g., `` `bg-${color}-500` ``).
Tailwind's scanner cannot detect them. Always use complete class strings or map from a lookup
object.

---

## Error Handling Patterns

### Component-Level Error Boundary

```svelte
<!-- +error.svelte -->
<script lang="ts">
  import { page } from '$app/stores';
</script>

<div class="flex flex-col items-center justify-center py-24 px-8 text-center">
  <div class="rounded-base border-2 border-black shadow bg-error-100 p-6 max-w-md w-full">
    <p class="text-xss font-black uppercase tracking-wider text-error-900 mb-2">
      Error {$page.status}
    </p>
    <h1 class="text-2xl font-black text-error-900 mb-3">{$page.error?.message ?? 'Something went wrong'}</h1>
    <a href="/" class="btn bg-error-600 text-white border-2 border-black shadow-small shadow-click-small rounded-base font-bold uppercase">
      Go Home
    </a>
  </div>
</div>
```

### Inline Async Error Handling in Components

```svelte
<script lang="ts">
  let result = $state<ApiResult<RunDetail> | null>(null);
  let loading = $state(false);

  async function load(uid: string) {
    loading = true;
    result = await getRun(uid);
    loading = false;
  }
</script>

{#if loading}
  <div class="h-32 bg-surface-200 rounded-base border-2 border-black animate-pulse" />
{:else if result?.ok === false}
  <div class="warn-color rounded-base border-2 border-black p-4 text-sm font-bold">
    {result.error}
  </div>
{:else if result?.ok}
  <RunDetail run={result.data} />
{/if}
```

---

## Code Style Rules

### Naming

| Thing | Convention | Example |
|---|---|---|
| Components | PascalCase | `RunTable.svelte` |
| Functions | camelCase | `fetchRuns`, `formatDate` |
| Types / Interfaces | PascalCase | `RunSummary`, `ApiResult<T>` |
| Constants | UPPER_SNAKE | `MAX_PAGE_SIZE`, `DEFAULT_SORT` |
| State modules | camelCase + `.svelte.ts` | `selection.svelte.ts` |
| Route params | kebab-case | `[run-uid]` |
| Utility files | kebab-case | `format.ts`, `debounce.ts` |

### Import Order

```typescript
// 1. SvelteKit / Svelte built-ins
import { goto } from '$app/navigation';
import { page } from '$app/stores';

// 2. Third-party
import { ExternalLink } from 'lucide-svelte';

// 3. Internal — absolute ($lib/...)
import { api } from '$lib/api/client';
import type { RunSummary } from '$lib/types';

// 4. Internal — relative
import RunRow from './RunRow.svelte';
```

### File Structure

```
src/
  lib/
    api/          # typed fetch wrappers (client.ts, runs.ts, ...)
    state/        # shared reactive state (*.svelte.ts)
    utils/        # pure utilities (format.ts, debounce.ts, url.ts, cx.ts)
    types/        # shared type definitions (index.ts)
    components/
      ui/          # generic reusable (Badge, Pill, Modal, ...)
      runs/        # feature-specific (RunTable, RunRow, RunDetail, ...)
      trace/       # trace-specific (TraceWaterfall, SpanRow, ...)
  routes/
    (app)/         # layout group with shared nav
      runs/
        +page.svelte
        +page.server.ts
        [uid]/
          +page.svelte
          +page.server.ts
    api/           # API route handlers
      runs/
        +server.ts
        [uid]/
          +server.ts
```

---

## Anti-Patterns — Never Do These

| Violation | Correct Alternative |
|---|---|
| `$:` reactive statements | `$derived(() => ...)` rune |
| `writable()` / `readable()` stores | `$state` in `.svelte.ts` module |
| `on:click=` event directive | `onclick=` attribute |
| `any` type | `unknown` + type narrowing |
| Arbitrary hex in `style=` | opsml-theme CSS variables via Tailwind |
| Dynamic partial class names `` `bg-${x}-500` `` | Full class string lookup map |
| Sequential `await` inside a single effect | `Promise.all` for parallel fetches |
| Un-keyed `{#each}` on mutable lists | `{#each items as item (item.uid)}` |
| Mutating props directly | Emit via callback prop; parent owns state |
| `document.querySelector` in components | Bind element with `bind:this` |
| `localStorage` for server-side-rendered routes | URL params or cookies via `locals` |
| Throwing raw errors from load functions | `throw error(status, message)` from `@sveltejs/kit` |
