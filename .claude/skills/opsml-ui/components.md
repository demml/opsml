# OpsML UI Component Reference

**UI root**: `crates/opsml_server/opsml_ui/src/`

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
    ├── agent/                # Agent overview
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
| `agent/AgentDashboard.svelte` | Agent eval dashboard |
| `agent/record/EvalRecordTable.svelte` | Record list |
| `agent/record/EvalRecordContent.svelte` | Record detail |
| `agent/workflow/AgentEvalWorkflowTable.svelte` | Workflow list |
| `agent/task/AgentTaskAccordion.svelte` | Collapsible task list |
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
datacard.ts        // DataCard + nested interface types
modelcard.ts       // ModelCard + save metadata
experimentcard.ts  // ExperimentCard + params/metrics
promptcard.ts      // PromptCard + eval profile
servicecard.ts     // ServiceCard
enum.ts            // AnyCard union type, RegistryType enum
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
- Monitoring: `lib/server/scouter/agent/utils.ts`, `drift/utils.ts`
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
| Agent monitoring | `AgentDashboard.svelte` |
| Drift monitoring | `PsiDashboard`, `SpcDashboard`, or `CustomDashboard` |
| Trace waterfall | `TraceDashboard.svelte` |
| Dropdown select | `Dropdown.svelte` (simple) or `ComboBoxDropDown.svelte` (searchable) |
| Two-column page | `grid grid-cols-1 lg:grid-cols-3` pattern |
| New card detail tab | Add under `[registry]/card/[space]/[name]/[version]/` + register in layout |
| New registry route | Mirror existing `[registry]` pattern; add layout + page server + page |
