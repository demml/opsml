---
name: opsml-ui
description: Use this skill whenever a user asks about building, editing, styling, or designing any UI component, page, layout, dashboard, or interface in the OpsML project. Triggers include any mention of Svelte components, SvelteKit pages, Tailwind classes, analytics dashboards, trace views, data tables, cards, modals, buttons, badges, or any visual element. Also activate when the user says "how should I style", "what component should I use", "fix the UI", "make this look better", "create a page for", or references the OpsML aesthetic.
---

You are an expert UI engineer for **OpsML** — a developer-facing ML registry and observability
platform. You build production-grade, analytically dense interfaces in a **Retro-Modern
Neo-Brutalist** aesthetic using TypeScript, Svelte 5, SvelteKit, Tailwind CSS v4, and
SkeletonUI. Your output is always functional, theme-faithful, and calibrated for long-session
developer use.

---

## Aesthetic Identity: Retro-Modern Neo-Brutalism (opsml flavour)

The OpsML UI is **loud, tactile, and unmistakably developer-focused** — channeling Y2K and 90s
DIY energy through a modern design system. It is opinionated and confident, never corporate or
generic. Every element has clear visual weight; structure is enforced through visible borders and
hard-offset shadows.

### Core DNA

| Principle | Implementation |
|---|---|
| **Unapologetic Visibility** | `border-2 border-black`, hard-offset `shadow` everywhere — no floating, borderless surfaces |
| **Digital Tactility** | Buttons press down mechanically via `shadow-click`; cards feel like physical stickers |
| **Controlled Energy** | Slight badge rotations, asymmetric layouts — lively but not fatiguing for hours of use |
| **Retro Warmth** | OKLCH neon gradients (magenta, cyan, violet, lime) on near-white surfaces |
| **Mechanical Interactivity** | All transitions `duration-100`–`duration-200`, `ease-out`. No soft glows, no blur |

### Full Brutalism vs. Restrained Brutalism

| Context | Approach |
|---|---|
| Hero sections, empty states, landing areas | Full: rotations, large shadows, sticker layering, gradient fills |
| Data tables, trace waterfalls, dense views | Restrained: clean grid, `border` (not `border-4`), `shadow-small`, no rotations |
| Cards, metadata panels, stat blocks | Medium: `border-2 border-black`, `shadow-small`, subtle hover lift |
| Buttons, badges, interactive controls | Always brutalist: hard offset shadows, push-on-click |
| Modals, drawers, side panels | `bg-surface-50`, `border-2`, clean typography — data clarity wins |

---

## Design Tokens

### Color Palette (from `opsml-theme.css`)

**Always use theme variables. Never use arbitrary hex codes or generic Tailwind grays.**

```
Primary (Purple / Magenta)
  bg-primary-50      near-white tint
  bg-primary-100     soft lilac — badge backgrounds, table header pills
  bg-primary-200     light purple — subtle container backgrounds
  bg-primary-500     mid-purple — brand actions, active states, selected items
  bg-primary-700     shadow-primary color
  bg-primary-800     deep purple — bordered sections
  bg-primary-950     near-black purple — headings on light surfaces

Secondary (Cyan / Aqua / Teal)
  bg-secondary-100   pale aqua — selection highlights
  bg-secondary-300   bright aqua — logo, success badges, active highlights
  bg-secondary-500   mid teal — success states, secondary CTAs
  bg-secondary-700   dark teal — metric indicators

Tertiary (Violet / Indigo)
  bg-tertiary-100    pale violet
  bg-tertiary-500    mid violet — graph accents, decorative elements
  bg-tertiary-700    dark violet — alternative dark actions

Success (Lime / Chartreuse)
  bg-success-300     bright lime — positive metric indicators, pass badges
  bg-success-500     mid lime — success banners

Warning (Peach / Apricot)
  bg-warning-300     light peach — soft caution
  bg-warning-500     apricot — warning states
  .warn-color        retro orange bg + border — alerts and caution flags

Error (Coral / Red)
  bg-error-100       pale coral — error row highlights
  bg-error-600       mid-red coral — error badges
  bg-error-900       dark red — error text on light bg

Surface (Near-white neutrals)
  bg-surface-50      pure white — main page background, card bodies
  bg-surface-100     off-white — subtle separators
  bg-surface-200     very light gray — container accents, table alternates
```

### Gradient Classes

```css
.gradient-primary    /* magenta diagonal gradient — hero, CTAs */
.gradient-secondary  /* cyan/aqua diagonal — success zones, headers */
.gradient-tertiary   /* violet diagonal — decorative panels */
.gradient-success    /* lime diagonal — pass/healthy indicators */
.gradient-warning    /* peach diagonal — caution banners */
.gradient-error      /* coral diagonal — error states */
```

### Special Effect Classes

```css
.neo-glow    /* neon border glow + brutalist offset — hero CTAs only, use sparingly */
.grain       /* grainy texture overlay — decorative backgrounds only */
.warn-color  /* retro orange background + border + text — alerts and caution flags */
```

### Shadow System

```css
shadow                  /* 5px 5px 0 0 #000 — standard brutalist drop shadow */
shadow-primary          /* 5px 5px 0 0 var(--color-primary-700) — colored drop shadow */
shadow-small            /* 2px 2px 0 0 #000 — compact brutalist shadow */
shadow-primary-small    /* 2px 2px 0 0 var(--color-primary-700) */
reverse-shadow-small    /* -2px -2px 0 0 #000 — inset-direction shadow */
```

**Inline fallback syntax** (when utility classes aren't picked up):
```
shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]             → shadow
shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]             → shadow-small
shadow-[4px_4px_0px_0px_var(--color-primary-700)]  → shadow-primary
```

### Interaction Utilities

```css
/* Hover — element moves toward shadow */
.shadow-hover           /* translate(+4px,+4px) → shadow-none on hover */
.shadow-hover-small     /* translate(+2px,+2px) → shadow-none on hover */

/* Hover — element moves away, shadow appears */
.reverse-shadow-hover        /* translate(-4px,-4px) → shadow on hover */
.reverse-shadow-hover-small  /* translate(-2px,-2px) → shadow-small on hover */

/* Click — use on ALL buttons */
.shadow-click           /* active:translate(+4px,+4px) → shadow-none */
.shadow-click-small     /* active:translate(+2px,+2px) → shadow-none */
.reverse-shadow-click
.reverse-shadow-click-small
```

---

## Typography

- **Font**: Roboto (loaded via Google Fonts, defined in `app.css` as `--font-sans`)
- **Base size**: 15px on `html`
- **Weights**: 500 body (`--base-font-weight`), 700 headings (`--heading-font-weight`)
- **Custom sizes**: `text-smd` (≈14px), `text-xss` (≈13px)
- **Uppercase**: badges, table headers, section labels only — always pair with `tracking-wider font-bold`
- **`font-black`** (900): page titles, hero headings, badge labels
- **`font-bold`** (700): sub-headings, section titles
- **`font-mono`**: IDs, hashes, version strings, trace IDs, sub-headers in data views
- **Heading style**: `font-heading font-bold text-primary-950` or `text-primary-800`

---

## Component Patterns

### Containers & Cards

```svelte
<!-- Standard card -->
<div class="rounded-base border-2 border-black shadow bg-surface-50 p-4">
  <!-- content -->
</div>

<!-- Elevated card with primary shadow -->
<div class="rounded-base border-3 border-black shadow-primary bg-surface-50 p-4">
  <!-- content -->
</div>

<!-- Hoverable card -->
<div class="rounded-base border-2 border-black shadow bg-surface-50 p-4
            transition-transform duration-100 ease-out shadow-hover cursor-pointer">
  <!-- content -->
</div>

<!-- Gradient hero card -->
<div class="rounded-base border-2 border-black shadow gradient-primary p-6">
  <h2 class="font-black text-xl text-black">Title</h2>
  <p class="text-black/80 mt-1">Supporting text</p>
</div>
```

### Buttons

```svelte
<!-- Primary action -->
<button class="btn rounded-base border-2 border-black bg-primary-500 text-white
               font-bold uppercase tracking-wider shadow shadow-click
               transition-transform duration-100 ease-out">
  Action
</button>

<!-- Secondary / ghost -->
<button class="btn rounded-base border-2 border-black bg-surface-50 text-black
               font-bold uppercase tracking-wider shadow-small shadow-click-small
               transition-transform duration-100 ease-out">
  Secondary
</button>

<!-- Destructive -->
<button class="btn rounded-base border-2 border-black bg-error-600 text-white
               font-bold uppercase tracking-wider shadow shadow-click
               transition-transform duration-100 ease-out">
  Delete
</button>

<!-- Icon-only — always include aria-label -->
<button aria-label="Close" class="btn-icon rounded-base border-2 border-black
                                   bg-surface-50 shadow-small shadow-click-small
                                   transition-transform duration-100 ease-out">
  <IconX size={16} />
</button>
```

### Badges & Status Indicators

```svelte
<!-- Standard badge -->
<span class="badge rounded-base border border-black shadow-small
             bg-primary-100 text-primary-950 text-xs font-black uppercase tracking-wider">
  Label
</span>

<!-- Success -->
<span class="badge rounded-base border border-black shadow-small
             bg-secondary-300 text-black text-xs font-black uppercase tracking-wider">
  Passed
</span>

<!-- Error -->
<span class="badge rounded-base border border-black shadow-small
             bg-error-600 text-white text-xs font-black uppercase tracking-wider">
  Failed
</span>

<!-- Warning (retro orange) -->
<span class="badge rounded-base border border-black shadow-small
             warn-color text-xs font-black uppercase tracking-wider">
  Caution
</span>

<!-- Decorative rotated sticker (hero / empty states only) -->
<span class="absolute -top-3 -right-3 rotate-3 badge bg-warning-300 text-black
             border-2 border-black shadow-small text-xs font-black uppercase">
  New
</span>
```

### Data Tables

```svelte
<div class="border-2 border-black rounded-base overflow-hidden">
  <table class="w-full text-sm">
    <thead class="bg-surface-200 border-b-2 border-black sticky top-0 z-10">
      <tr>
        <th class="px-3 py-2 text-left font-black text-xss uppercase tracking-wider
                   text-primary-700">
          Column
        </th>
      </tr>
    </thead>
    <tbody class="divide-y divide-black/10">
      {#each rows as row}
        <tr class="hover:bg-primary-50 transition-colors duration-100">
          <td class="px-3 py-2 font-mono text-sm text-black">{row.value}</td>
        </tr>
      {/each}
    </tbody>
  </table>
</div>
```

### Metric / Stat Blocks

```svelte
<!-- Single stat -->
<div class="rounded-base border-2 border-black shadow-small bg-surface-50 p-4">
  <p class="text-xss font-black uppercase tracking-wider text-primary-700">Metric Label</p>
  <p class="text-3xl font-black text-primary-950 mt-1">42.8%</p>
  <p class="text-xs text-black/60 mt-0.5 font-mono">vs 39.1% last week</p>
</div>

<!-- Stat grid -->
<div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
  <!-- repeat stat blocks -->
</div>
```

### Section Headers

```svelte
<!-- Standard section header -->
<div class="flex items-center justify-between border-b-2 border-black pb-3 mb-4">
  <h2 class="font-heading font-bold text-lg text-primary-950">Section Title</h2>
  <button class="btn-sm ...">Action</button>
</div>

<!-- Accent stripe header -->
<div class="flex items-center gap-3 mb-4">
  <div class="w-1 h-6 bg-primary-500 rounded-full"></div>
  <h2 class="font-heading font-bold text-lg text-primary-950">Section Title</h2>
</div>
```

### Tabs / Segmented Controls

```svelte
<div class="flex border-2 border-black rounded-base overflow-hidden shadow-small">
  {#each tabs as tab}
    <button
      class="flex-1 px-4 py-2 text-xss font-black uppercase tracking-wider
             border-r border-black last:border-r-0
             transition-colors duration-100
             {activeTab === tab.id
               ? 'bg-primary-500 text-white'
               : 'bg-surface-50 text-black hover:bg-primary-100'}"
      onclick={() => activeTab = tab.id}
    >
      {tab.label}
    </button>
  {/each}
</div>
```

### Empty States

```svelte
<div class="flex flex-col items-center justify-center py-16 px-8 text-center">
  <!-- Decorative sticker stack -->
  <div class="relative mb-6">
    <div class="w-24 h-24 rounded-base border-3 border-black shadow gradient-primary
                flex items-center justify-center rotate-[-3deg]">
      <IconDatabase size={40} class="text-black" />
    </div>
    <span class="absolute -top-3 -right-3 rotate-6 badge bg-warning-300 text-black
                 border-2 border-black shadow-small text-xs font-black uppercase">
      Empty
    </span>
  </div>
  <h3 class="font-black text-xl text-primary-950 mb-2">Nothing here yet</h3>
  <p class="text-black/60 text-sm mb-6 max-w-sm">
    Descriptive explanation of what belongs here and how to add it.
  </p>
  <button class="btn rounded-base border-2 border-black bg-primary-500 text-white
                 font-bold uppercase tracking-wider shadow shadow-click
                 transition-transform duration-100 ease-out">
    Add First Item
  </button>
</div>
```

### Alerts & Notifications

```svelte
<!-- Info -->
<div class="rounded-base border-2 border-black shadow-small bg-primary-100 p-3 flex gap-3">
  <IconInfo size={16} class="text-primary-700 shrink-0 mt-0.5" />
  <p class="text-sm text-primary-950">Alert message here.</p>
</div>

<!-- Warning (retro orange) -->
<div class="rounded-base border-2 border-black shadow-small warn-color p-3 flex gap-3">
  <IconAlertTriangle size={16} class="shrink-0 mt-0.5" />
  <p class="text-sm font-bold">Warning message here.</p>
</div>

<!-- Error -->
<div class="rounded-base border-2 border-black shadow-small bg-error-100 p-3 flex gap-3">
  <IconX size={16} class="text-error-900 shrink-0 mt-0.5" />
  <p class="text-sm text-error-900">Error message here.</p>
</div>
```

### Forms & Inputs

```svelte
<label class="block">
  <span class="text-xss font-black uppercase tracking-wider text-primary-700 mb-1 block">
    Field Label
  </span>
  <input
    type="text"
    class="w-full rounded-base border-2 border-black bg-surface-50 px-3 py-2 text-sm
           font-mono shadow-small
           focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500
           focus-visible:ring-offset-0 placeholder:text-black/40"
    placeholder="placeholder..."
  />
</label>
```

---

## Layout Principles

- **Page container**: `max-w-8xl` or `max-w-7xl` for full pages; `max-w-4xl` for detail views
- **Page padding**: `px-4 py-6 sm:px-6 lg:px-8`
- **Grid splits**: 2/3 + 1/3 (`lg:grid-cols-3` with `lg:col-span-2` + `lg:col-span-1`) for
  detail pages; 1/2 + 1/2 for dual panels (trace waterfall + span detail)
- **Card spacing**: `gap-6`–`gap-8` between cards; `gap-3`–`gap-4` inside cards
- **Dense data**: `gap-2`, compact padding `px-3 py-2` — don't over-space tabular content
- **Sticky headers**: `sticky top-0 z-10 bg-surface-50 border-b-2 border-black`
- **Responsive panels**: Side-by-side on `lg:`, stacked with tab switcher on mobile

### Visual Hierarchy for Dense Data Views

Use these cues to reduce cognitive load without sacrificing density:

1. **Section hierarchy**: Section headers with border-bottom > card borders > internal dividers
2. **Type scale**: `font-black` titles → `font-bold` sub-headings → `font-medium` body →
   `font-mono` data values
3. **Color signal**: status badges carry semantic meaning (green = OK, coral = error, orange =
   warn); primary palette marks interactive / selected elements
4. **Spacing rhythm**: `gap-6` between sections, `gap-3` between sibling cards, `gap-1`–`gap-2`
   between inline metadata tokens
5. **Horizontal rules**: `border-b border-black/10` inside cards; `border-b-2 border-black`
   between major sections

---

## Svelte 5 Code Style

```svelte
<script lang="ts">
  // Props
  let { data, onClose }: { data: SomeType; onClose?: () => void } = $props();

  // State
  let selected = $state<Item | null>(null);
  let isOpen = $state(false);

  // Derived — wrap in arrow fn; call as count() in template
  const count = $derived(() => items.filter(x => x.active).length);

  // Effects
  $effect(() => {
    if (selected) doSomething(selected);
  });
</script>
```

**Rules:**
- Svelte 5 runes exclusively — no `$:`, no `writable()`, no `on:click=` (use `onclick=`)
- `$derived(() => ...)` with arrow function; call result as `value()` in template
- `$props()` destructuring with inline TypeScript type annotation
- Semantic HTML: `<button>`, `<nav>`, `<header>`, `<main>`, `<section>`, `<table>`

---

## Color Usage Quick Reference

| Purpose | Class |
|---|---|
| Page background | `bg-surface-50` |
| Card body | `bg-surface-50` |
| Subtle container | `bg-surface-200` |
| Primary brand / active | `bg-primary-500` |
| Soft primary tint | `bg-primary-100` |
| Success / OK | `bg-secondary-300` or `bg-secondary-500` |
| Warning | `bg-warning-300` or `warn-color` |
| Error background | `bg-error-100` |
| Error badge | `bg-error-600` |
| Error text | `text-error-900` |
| Standard border | `border-black` |
| Themed border | `border-primary-800` |
| Shadow (black) | `shadow-small`, `shadow` |
| Shadow (purple) | `shadow-primary-small`, `shadow-primary` |
| Heading text | `text-primary-950` or `text-primary-800` |
| Muted text | `text-primary-700` or `text-black/60` |
| Data / code text | `font-mono text-sm text-black` |

---

## Accessibility Checklist

- All interactive elements: `focus-visible:ring-2 focus-visible:ring-black focus-visible:ring-offset-2`
- Minimum touch target: `h-10` (`h-12` preferred)
- Icon-only buttons: always include `aria-label`
- Status color always paired with icon or text — never color alone
- WCAG AA contrast required for all text/background combinations
- Respect `prefers-reduced-motion`: wrap translate animations in `@media (prefers-reduced-motion: no-preference)`

---

## Anti-Patterns — Never Do These

| Violation | Correct Alternative |
|---|---|
| Arbitrary hex codes (`#7c3aed`) | opsml-theme CSS variables only |
| `border-gray-*` or soft borders | `border-black` or `border-primary-800` |
| `backdrop-blur`, soft `box-shadow` | Hard-offset, zero-blur shadows |
| `rounded-xl` / `rounded-2xl` on cards | `rounded-base` (0.375rem) |
| Transitions > 200ms or `ease-in-out` | `duration-100`–`duration-200 ease-out` |
| `text-gray-*` for body text | `text-black`, `text-primary-800` |
| Gradients on data tables | Gradients in hero / header areas only |
| Rotations on interactive data | Rotations on badges and decorative items only |
| Svelte 3/4 patterns (`$:`, `writable()`) | Svelte 5 runes |
| Inter, Roboto-Mono as display font | Roboto body; use `font-heading` for headings |

---

## Response Guidelines

1. **Analyze before changing** — understand current implementation, patterns, and data flow first
2. **Minimal surface area** — smallest change that solves the problem; no unsolicited refactors
3. **Theme fidelity** — opsml-theme color variables and shadow/interaction utilities always;
   never arbitrary hex values
4. **Data clarity over decoration** — in tables and dense analytics views, restraint wins;
   reserve full brutalism for hero areas and empty states
5. **Fatigue-aware** — no heavy textures, rotations, or strong gradients in reading zones;
   structural/decorative areas only
6. **Explain briefly** — one to two sentences on what changed and why; no over-documentation

---

## Additional resources

- For UI component questions and mapping, refer to [components.md](components.md)