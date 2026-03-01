---
name: opsml-ui-components
description: Use this skill whenever a user asks about building, editing, styling, or designing any UI component, page, layout, dashboard, or interface in the OpsML project. Triggers include any mention of Svelte components, SvelteKit pages, Tailwind classes, analytics dashboards, trace views, data tables, cards, modals, buttons, badges, or any visual element. Also activate when the user says "how should I style", "what component should I use", "fix the UI", "make this "look better", "create a page for", or references the OpsML aesthetic.
---

You are an expert in the OpsML SvelteKit UI codebase. Use this reference map to quickly locate the right component, understand patterns, and apply the correct design system without reading every file from scratch.

**UI root**: `crates/opsml_server/opsml_ui/src/`

---

## Design System (Non-Negotiable Rules)

OpsML uses a **Neo-Brutalist** aesthetic via Tailwind CSS v4 + `opsml-theme.css` + Skeleton Labs.

### Core CSS Conventions
- **Borders**: `border-2 border-black` or `border-primary-800` — never `border-gray-*`
- **Shadows**: Hard-offset, never soft or blurred
  - `.shadow` → `5px 5px 0px 0px black`
  - `.shadow-small` → `2px 2px 0px 0px black`
  - `.shadow-primary` → same, primary color
  - `.shadow-hover` → translate on hover (removes shadow illusion)
  - `.shadow-click` → translate on active
  - `.reverse-shadow-*` → negative-direction offsets
- **Border radius**: `rounded-base` (0.375rem max) — no `rounded-xl`, no `rounded-full` except avatars
- **Backgrounds**: `bg-surface-50` for cards/pages; theme palette for accents — no arbitrary hex
- **Transitions**: `duration-100` or `duration-200` with `ease-out` only — no slow/elastic animations
- **No**: `backdrop-blur`, soft shadows, `border-gray-*`, arbitrary hex colors

### Color Palette
- `primary-*` — Purple brand (#5948a3 range)
- `success-*` — Green for positive/active states
- `error-*` — Red for errors/alerts
- `warning-*` — Yellow for warnings
- `surface-50/100` — Page and card backgrounds

### Standard Card Pattern
```svelte
<div class="bg-surface-50 border-2 border-black shadow rounded-base p-4">
  ...
</div>
```

### Standard Two-Column Layout
```svelte
<div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
  <div class="lg:col-span-2"><!-- main content --></div>
  <div class="lg:col-span-1"><!-- sidebar --></div>
</div>
```

### Buttons
```svelte
<button class="btn bg-primary-500 text-black border-2 border-black shadow shadow-hover">
```

### Typography
- Font: Roboto (Google Fonts, already loaded)
- `font-bold` / `font-black` for hero text
- `font-mono` for IDs, versions, code

### Grid Responsive Breakpoints
- Mobile → `grid-cols-1`
- `md:grid-cols-2` → `lg:grid-cols-3` → `2xl:grid-cols-4`

---

## Svelte 5 Patterns (Required — No Legacy Syntax)

```svelte
<script lang="ts">
  // Props
  let { name, items = $bindable() } = $props<{ name: string; items: string[] }>();

  // State
  let count = $state(0);

  // Derived
  let doubled = $derived(count * 2);
  let sorted = $derived.by(() => [...items].sort());

  // Effects
  $effect(() => {
    console.log(count);
  });
</script>

<!-- Events: use direct handlers, not on:click= -->
<button onclick={() => count++}>Click</button>
```

**Banned patterns**: `$:`, `writable()`, `on:click=`, `createEventDispatcher`

---

## Route Map

```
src/routes/
├── +layout.svelte            # Root: Navbar + ToastProvider + grid bg
├── +layout.server.ts         # Loads user, inits userStore
└── opsml/
    ├── home/                 # Dashboard with stats + recent cards
    ├── user/                 # login, register, profile, logout, reset, sso/callback
    ├── space/                # Space list + [space]/ detail
    ├── [registry]/           # Card listing (data, model, experiment, prompt, service)
    │   └── card/[space]/[name]/[version]/
    │       ├── +layout.svelte  # Tab nav (card, files, versions, monitoring)
    │       ├── card/           # Main card overview
    │       ├── files/          # File browser + viewer
    │       ├── versions/       # Version history
    │       ├── readme/         # README editor
    │       ├── metrics/        # Experiment metrics
    │       ├── hardware/       # Hardware stats
    │       └── monitoring/     # PSI, SPC, custom drift
    ├── genai/                # GenAI overview
    │   ├── prompt/[registry]/...  # Prompt cards + evaluation/
    │   ├── agent/[registry]/...   # Agent cards + playground/ + evaluation/
    │   └── eval/             # Evaluation summary
    └── observability/        # Trace waterfall dashboard
        └── [traceId]/        # Trace detail with spans

src/routes/api/               # Internal SvelteKit API proxies (card, space, user, scouter)
```

**Dynamic params**: `[registry]`, `[space]`, `[name]`, `[version]`, `[...file]` (rest param)

---

## Component Directory

### Navigation — `lib/components/nav/`
| Component | Purpose |
|-----------|---------|
| `Navbar.svelte` | Top nav bar; reads `$page` for active state |
| `Sidebar.svelte` | Collapsible sidebar with hover-expand + pin toggle |

### Card Display — `lib/components/card/`
| Component | Purpose | Key Props |
|-----------|---------|-----------|
| `CardPage.svelte` | Single card in grid (name, space, version, time) | `name, space, version, registry, updated_at, nbr_versions, bgColor` |
| `CardPageView.svelte` | Grid of cards with pagination | `registryPage, registry, onPageChange?` |
| `CardTableView.svelte` | Table view of cards | `registryPage, registry, onPageChange?` |
| `CardSearch.svelte` | Search/filter UI | — |
| `CardReadMe.svelte` | README display with markdown | — |
| `VersionButton.svelte` | Version selector dropdown | — |
| `VersionPage.svelte` | Full version history | — |

### Card Type Pages — `lib/components/card/{type}/`
| Component | Props |
|-----------|-------|
| `data/DataPage.svelte` | `data: { metadata: DataCard, readme }` |
| `model/ModelPage.svelte` | `data: { metadata: ModelCard, savedata }` |
| `experiment/ExperimentPage.svelte` | `data: { metadata: ExperimentCard, parameters }` |
| `prompt/PromptPage.svelte` | `data: { metadata: PromptCard }` |
| `service/ServicePage.svelte` | `data: { metadata: ServiceCard }` |
| `agent/AgentPage.svelte` | Agent spec, capabilities, skills, playground |

### Card Layouts — `lib/components/card/layouts/`
Five two-column layout wrappers: `DataCardLayout`, `ModelCardLayout`, `ExperimentCardLayout`, `PromptCardLayout`, `ServiceCardLayout`

### Data Visualization — `lib/components/card/`
| Component | Purpose |
|-----------|---------|
| `data/DataProfileViz.svelte` | Data profile visualization |
| `data/NumericStats.svelte` | Numeric feature stats |
| `data/StringStats.svelte` | String feature stats |
| `data/FeaturePill.svelte` | Feature type badge |
| `experiment/MetricTable.svelte` | Sortable metrics table |
| `experiment/MetricComparisonTable.svelte` | Compare metrics across versions |
| `experiment/ParameterTable.svelte` | Experiment parameters |
| `experiment/FigureViz.svelte` | Figure embed |

### Agent Components — `lib/components/card/agent/`
| Component | Purpose |
|-----------|---------|
| `AgentMetadata.svelte` | Agent name/version/docs |
| `AgentCapabilities.svelte` | Capabilities list |
| `AgentSkills.svelte` | Available skills |
| `AgentCards.svelte` | Associated data/model cards |
| `AgentAuthConfig.svelte` | Auth requirements |
| `EnhancedAgentPlayground.svelte` | Interactive agent tester |
| `DebugPayloadSidebar.svelte` | Request/response inspector |
| `evaluation/AgentEvalDashboard.svelte` | Eval dashboard |
| `evaluation/AgentEvalRecordTable.svelte` | Paginated eval records |

### Prompt Components — `lib/components/card/prompt/`
| Component | Purpose |
|-----------|---------|
| `PromptEvalDashboard.svelte` | Evaluation dashboard |
| `common/PromptViewer.svelte` | Render prompt (system + messages) |
| `common/PromptModal.svelte` | Full prompt modal |
| `common/MessageBubble.svelte` | Single chat message |
| `common/EvalTasksModal.svelte` | Eval tasks list |

### File Handling — `lib/components/files/`
| Component | Purpose | Key Props |
|-----------|---------|-----------|
| `FileViewer.svelte` | Routes to correct viewer by type | `file: RawFile` |
| `CodeViewer.svelte` | Syntax-highlighted code | `content, language` |
| `MarkdownViewer.svelte` | Markdown → HTML | — |
| `ImageViewer.svelte` | Image display | — |
| `FileTree.svelte` | Hierarchical file browser | — |

### Observability / Traces — `lib/components/trace/`
| Component | Purpose | Key Props |
|-----------|---------|-----------|
| `TraceDashboard.svelte` | Main dashboard with live polling | `trace_page, trace_metrics, initialFilters` |
| `TraceTable.svelte` | Paginated trace list | — |
| `TraceWaterfall.svelte` | Span waterfall viz | — |
| `TraceCharts.svelte` | Metrics time series | — |
| `TimeRangeFilter.svelte` | Time range presets | — |
| `SpanDetailView.svelte` | Span details panel | — |
| `graph/SpanGraph.svelte` | D3 dependency graph | — |

### Scouter Monitoring — `lib/components/scouter/`
| Component | Purpose |
|-----------|---------|
| `genai/GenAIDashboard.svelte` | GenAI eval dashboard |
| `genai/record/GenAIEvalRecordTable.svelte` | Record list |
| `genai/record/GenAIEvalRecordContent.svelte` | Record detail |
| `genai/workflow/GenAIEvalWorkflowTable.svelte` | Workflow list |
| `genai/task/GenAITaskAccordion.svelte` | Collapsible task list |
| `drift/PsiDashboard.svelte` | PSI drift monitoring |
| `drift/SpcDashboard.svelte` | SPC monitoring |
| `drift/CustomDashboard.svelte` | Custom metrics |
| `update/UpdateModal.svelte` | Update monitoring config modal |
| `ScouterRequiredView.svelte` | Shown when Scouter not configured |

### Utility Components — `lib/components/utils/`
| Component | Purpose | Key Props |
|-----------|---------|-----------|
| `Pill.svelte` | Key-value badge | `key, value, textSize, borderColor?, textColor?, bgColor?` |
| `LinkPill.svelte` | Clickable pill with URL | — |
| `Dropdown.svelte` | Generic dropdown | `items: {label, value}[], selectedValue, onSelect` |
| `ComboBoxDropDown.svelte` | Searchable dropdown | — |
| `MultiComboBoxDropDown.svelte` | Multi-select searchable | — |
| `VirtualScroller.svelte` | Virtual scroll for large lists | — |
| `Warning.svelte` | Warning message | — |

### Visualization — `lib/components/viz/`
| Component | Purpose | Key Props |
|-----------|---------|-----------|
| `Chart.svelte` | Bar/line chart (Chart.js + zoom) | `groupedMetrics, yLabel, plotType, resetZoomTrigger` |
| `HistChart.svelte` | Histogram | — |
| `TimeSeries.svelte` | Time series | — |
| `WordBarChart.svelte` | Horizontal bar (categorical) | — |

### README — `lib/components/readme/`
| Component | Purpose |
|-----------|---------|
| `Readme.svelte` | CodeMirror markdown editor + preview + save |
| `Markdown.svelte` | Markdown renderer (github-markdown-css) |
| `NoReadme.svelte` | Empty state CTA |

### Home / Dashboard — `lib/components/home/`
| Component | Purpose | Key Props |
|-----------|---------|-----------|
| `Homepage.svelte` | Stats grid + recent activity | `cards: RecentCards, stats: HomePageStats` |
| `HomeCard.svelte` | Recent cards for one registry | `header, cards, headerColor, headerTextColor, iconColor, badgeColor` |

### Space — `lib/components/space/`
`SpacePage.svelte`, `RecentCard.svelte`, `CreateSpaceModal.svelte`

### User — `lib/components/user/`
`UserDropdown.svelte`, `LoginWarning.svelte`, `UpdatePassword.svelte`, `LogoutModal.svelte`

### Code Display — `lib/components/codeblock/`
`CodeBlock.svelte` — syntax-highlighted code block

---

## Key Types — `lib/components/card/card_interfaces/`

```typescript
// Types live here:
datacard.ts     // DataCard + nested interface types
modelcard.ts    // ModelCard + save metadata
experimentcard.ts  // ExperimentCard + params/metrics
promptcard.ts   // PromptCard + eval profile
servicecard.ts  // ServiceCard
enum.ts         // AnyCard union type, RegistryType enum
```

**Pagination types** — `lib/components/card/types.ts`:
- `QueryPageResponse` — paginated card list
- `CardCursor` — pagination cursor + filters
- `CardSummary` — card metadata summary

---

## Utilities & Helpers

### Client Utils — `lib/utils.ts`
```typescript
RegistryType          // enum: data, model, experiment, prompt, service, mcp, agent
getRegistryPath()     // route path for registry type
calculateTimeBetween()  // "2 hours ago" relative time
debounce()            // debounce function
```

### API Client — `lib/api/internalClient.ts`
```typescript
createInternalApiClient(fetch)  // wraps fetch with /opsml/api/ base
// Methods: .get(), .post(), .put(), .delete()
```

Always use this from `+page.server.ts` — never call the API directly from components.

### Server-side Utils
- Card: `lib/server/card/utils.ts`
- User: `lib/server/user/utils.ts`
- Monitoring: `lib/server/scouter/genai/utils.ts`, `drift/utils.ts`
- Traces: `lib/server/trace/utils.ts`
- API client: `lib/server/api/opsmlClient.ts`

### File Detection — `lib/components/files/utils.ts`
```typescript
getFileTypeInfo(suffix, mimeType)
// returns: { type: 'image'|'markdown'|'code'|'other', language?, mimeType? }
```

---

## State Management

Svelte 5 rune-based reactive classes (`.svelte.ts` files):

```typescript
// lib/components/settings/settings.svelte.ts
class UiSettings {
  scouterEnabled = $state(false);
  ssoEnabled = $state(false);
  initialize(settings: UiSettings) { ... }
}

// lib/components/user/user.svelte.ts
class UserStore {
  username = $state('');
  favorite_spaces = $state([]);
  fromUserResponse(res) { ... }
}
```

Both are initialized at layout level and used across components via context/import.

---

## Authentication Flow

1. `hooks.server.ts` — validates JWT on every request; redirects to `/opsml/user/login` if invalid
2. `+layout.server.ts` — fetches user info, populates `userStore`
3. `handleFetch` — attaches JWT cookie as `Authorization: Bearer` on all server-side fetches
4. Token refresh — silent: new `Authorization` header in backend response → cookie updated
5. Public routes (login, register, healthcheck) bypass auth check

---

## Page Data Flow Pattern

```typescript
// +page.server.ts
export const load: PageServerLoad = async ({ params, fetch }) => {
  const client = createInternalApiClient(fetch);
  const metadata = await client.get(`/card/metadata?space=${params.space}`);
  return { metadata };
};

// +page.svelte
<script lang="ts">
  let { data } = $props<{ data: PageData }>();
</script>
```

---

## Quick Decision Guide

| Task | Use |
|------|-----|
| Show a key-value pair | `Pill.svelte` |
| Paginated list of cards | `CardPageView.svelte` (grid) or `CardTableView.svelte` |
| Render markdown | `Markdown.svelte` |
| Edit markdown | `Readme.svelte` (has CodeMirror editor) |
| File browser | `FileTree.svelte` → `FileViewer.svelte` |
| Chart (bar/line) | `Chart.svelte` with `groupedMetrics` |
| GenAI monitoring | `GenAIDashboard.svelte` |
| Drift monitoring | `PsiDashboard`, `SpcDashboard`, or `CustomDashboard` |
| Trace waterfall | `TraceDashboard.svelte` |
| Dropdown select | `Dropdown.svelte` (simple) or `ComboBoxDropDown.svelte` (searchable) |
| Two-column page | `grid grid-cols-1 lg:grid-cols-3` pattern |
| New card detail tab | Add under `[registry]/card/[space]/[name]/[version]/` + register in layout |
| New registry route | Mirror existing `[registry]` pattern; add layout + page server + page |
