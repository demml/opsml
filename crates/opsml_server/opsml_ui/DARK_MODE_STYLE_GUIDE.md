# OpsML Dark Mode Style Guide — Phosphor Terminal Green

Reference for all dark mode styling decisions. Based on the CRT terminal aesthetic.

---

## Core Principle

**Monochromatic green-on-black.** Every UI element uses a single hue (~150deg oklch) at varying lightness levels. The aesthetic is a vintage phosphor CRT monitor — text glows softly against a near-black void. No competing accent colors in decorative UI.

---

## Color Palette

### Backgrounds (darkest to lightest)

| Token | Value | Usage |
|---|---|---|
| `surface-950` | `oklch(5.5% 0.004 150)` | Page background — the deepest "CRT glass" black |
| `surface-900` | `oklch(6% 0.005 150)` | Recessed areas, footers |
| `surface-800` | `oklch(6.5% 0.005 150)` | Secondary panels |
| `surface-500` | `oklch(8% 0.007 150)` | Card backgrounds — barely elevated from page |
| `surface-200` | `oklch(10% 0.01 150)` | Nested sections within cards |
| `surface-100` | `oklch(11% 0.01 150)` | Hovered card areas |
| `surface-50` | `oklch(12% 0.01 150)` | Lightest surface — active/selected areas |

### Borders

| Context | Value | Notes |
|---|---|---|
| Card border | `oklch(25-30% 0.06 150)` | Thin 1px, low contrast — defines edges without shouting |
| Divider lines | `oklch(20-25% 0.05 150)` | Horizontal separators within cards |
| Input border | `oklch(30% 0.07 150)` | Slightly more visible for interactive elements |
| Focus ring | `oklch(55-65% 0.13 150)` | Visible green glow on focus |

### Text

| Role | Value | Usage |
|---|---|---|
| Primary text | `oklch(82% 0.14 152)` / `#8ddb9f` | All body copy, standard UI text |
| Heading text | `oklch(85-87% 0.15 150)` | Slightly brighter for h1-h3 |
| Muted/label text | `oklch(60-65% 0.10 150)` | Secondary labels, category headers, timestamps |
| Disabled text | `oklch(40-45% 0.08 150)` | Inactive/disabled elements |
| Bright accent | `oklch(90% 0.14 150)` | Hover state text, active links, emphasis |

### Fills (pills, badges, tags)

| Role | Value | Usage |
|---|---|---|
| Pill background | `oklch(20-25% 0.04 150)` | Metadata key-value pill fill |
| Badge fill | `oklch(28-32% 0.07 148)` | Tags, mode badges, status indicators |
| Active/selected fill | `oklch(36% 0.09 148)` | Selected tabs, active filters |
| Hover fill | `oklch(18-22% 0.03 150)` | Hover state on interactive pills |

---

## Component Rules

### Shadows

**Kill all box shadows in dark mode.** The reference has zero visible shadows. Cards are defined by borders alone, floating in darkness.

```css
/* Dark mode shadow override */
.theme-dark {
  --shadow: none;
  --shadow-small: none;
  --shadow-primary: none;
}
```

If a subtle glow is needed for elevation (modals, dropdowns), use a very faint green glow:
```css
box-shadow: 0 0 20px oklch(65% 0.14 150 / 0.08);
```

### Borders

Light mode uses thick `border-black` brutalist borders. Dark mode shifts to thin, atmospheric borders:

- **Width**: Always 1px (never 2px+ in dark mode)
- **Color**: `oklch(25-30% 0.06 150)` — green-tinted, low contrast
- **Radius**: Same as light mode (`--radius-base: 0.375rem`)
- **Never use** `border-black` literally — it must resolve to the green border

### Cards

```
┌─ 1px border oklch(28% 0.06 150) ─────────────────┐
│                                                     │
│  bg: surface-50 oklch(12% 0.01 150)               │
│                                                     │
│  ── section divider oklch(22% 0.04 150) ────────── │
│                                                     │
│  Nested section: surface-200 oklch(10% 0.01 150)  │
│                                                     │
└─────────────────────────────────────────────────────┘
```

- Background barely distinguishable from page
- Internal sections separated by 1px green dividers
- No shadow, no hard offset
- Nested sections use slightly different surface shade

### Navbar

- Background: continuous with page (`surface-950`)
- Logo: bold, heading-brightness green
- Nav links: standard phosphor green (`primary-800` / `oklch(75% 0.15 150)`)
- Active nav link: brightest green + possible underline
- Icons: `currentColor` (inherits phosphor green)
- Breadcrumb: muted green for path, brighter for linked segments

### Pills & Metadata Display

Key-value metadata uses filled pill shapes:

```
┌─────────────────────────────────────────┐
│ ┌──────────┐                            │
│ │ Label    │  Value text                │
│ └──────────┘                            │
└─────────────────────────────────────────┘
```

- **Label section**: Darker green fill (`oklch(20-25% 0.04 150)`) with rounded corners
- **Value text**: Standard phosphor green on card background
- **Overall pill**: Optional 1px border at `oklch(25% 0.05 150)`

### Tags & Badges

- Fill: `oklch(28-32% 0.07 148)` — visible but not loud
- Text: standard phosphor green
- Border: 1px, same hue, slightly lighter than fill
- Rounded corners, compact padding (`px-2.5 py-0.5`)
- No shadow, no gradient

### Buttons

| State | Background | Text | Border |
|---|---|---|---|
| Primary | `oklch(36% 0.09 148)` | `oklch(83% 0.15 150)` | 1px `oklch(45% 0.10 150)` |
| Primary hover | `oklch(40% 0.10 148)` | `oklch(90% 0.14 150)` | 1px `oklch(50% 0.11 150)` |
| Secondary | transparent | `oklch(75% 0.15 150)` | 1px `oklch(30% 0.06 150)` |
| Secondary hover | `oklch(15% 0.02 150)` | `oklch(83% 0.15 150)` | 1px `oklch(35% 0.07 150)` |
| Disabled | `oklch(12% 0.01 150)` | `oklch(40% 0.08 150)` | 1px `oklch(18% 0.03 150)` |

### Tables

- Header row: `surface-200` background, muted green text (uppercase/small)
- Row borders: 1px `oklch(18% 0.02 150)` — nearly invisible
- Alternating rows: optional, use `surface-100` vs `surface-50`
- Hover row: `oklch(14-16% 0.02 150)`
- Cell text: standard phosphor green

### Inputs & Form Controls

- Background: `surface-200` or slightly darker than card
- Border: 1px `oklch(30% 0.07 150)`
- Text: standard phosphor green
- Placeholder: muted green (`oklch(45-50% 0.08 150)`)
- Focus: border brightens to `oklch(55% 0.13 150)`, optional glow ring

### Tabs

- Inactive: muted green text, no background
- Active: bright green text, subtle underline or bottom border at `oklch(65% 0.14 150)`
- Hover: text brightens slightly
- No background fill change on tab switch

---

## Hover & Interaction States

| Interaction | Effect |
|---|---|
| Hover (text) | Brighten to `oklch(85-90% 0.14 150)` |
| Hover (card/row) | Background shifts to `oklch(14-16% 0.02 150)` |
| Hover (button) | Fill lightens ~4-5% in oklch lightness |
| Focus | Green border brightens + optional subtle glow ring |
| Active/pressed | Fill darkens slightly from hover state |
| Disabled | All values drop to `oklch(35-45%)` range, reduced chroma |

Transitions: `duration-100` / `duration-200` with `ease-out`. No slow or elastic animations.

---

## Semantic Colors in Dark Mode

Semantic colors exist but are **subdued** and **green-shifted** compared to light mode:

| Semantic | Dark Mode Treatment |
|---|---|
| **Success** | Same as primary green — no differentiation needed |
| **Warning** | Amber at `oklch(65-72% 0.12 60)` — visible but dimmer than green |
| **Error** | Muted red at `oklch(55-62% 0.14 14)` — desaturated, CRT-appropriate |
| **Info** | Use primary green or tertiary blue-gray |

These colors should only appear for functional UI (error messages, status badges). Decorative elements stay monochromatic green.

---

## Typography in Dark Mode

- Same font family as light mode (no change)
- `font-weight: 500` for body, `bold` for headings (same as light)
- Letter spacing: unchanged
- The green color itself creates the "terminal" feel — no need for monospace unless it's a code block

---

## Anti-Patterns (Never Do These in Dark Mode)

1. **No hard-offset box shadows** — dark mode has no shadows
2. **No `border-black`** resolving to actual black — must be green-tinted
3. **No `text-gray-*`** Tailwind defaults — always use themed green values
4. **No white or near-white text** — max brightness is `oklch(90%)` phosphor green
5. **No background colors above `oklch(15%)`** for surfaces — everything is near-black
6. **No multi-color accents** in decorative UI — monochromatic green only
7. **No thick borders (2px+)** — dark mode uses 1px exclusively
8. **No `backdrop-blur`** — irrelevant on near-black backgrounds
9. **No bright gradient fills** — retro gradients in dark mode are nearly invisible (`oklch(8-16%)`)
10. **No opacity-based darkening** (`bg-black/50`) — use explicit oklch surface values

---

## CSS Variable Mapping Cheat Sheet

When converting light-mode Tailwind classes to dark-mode-aware styles:

```
Light Mode Class        → Dark Mode Resolved Value
─────────────────────────────────────────────────────
text-black              → oklch(82% 0.14 152)  [phosphor green]
text-gray-600           → oklch(60% 0.10 150)  [muted green]
text-gray-900           → oklch(75% 0.15 150)  [bright green]
bg-surface-50           → oklch(12% 0.01 150)  [card bg]
bg-surface-100          → oklch(11% 0.01 150)  [slightly darker]
bg-white                → oklch(10% 0.01 150)  [dark surface]
border-black            → oklch(28% 0.06 150)  [subtle green]
border-gray-200         → oklch(20% 0.04 150)  [dim green]
shadow / shadow-small   → none
ring-primary-500        → oklch(55% 0.13 150)  [focus green]
```

---

## Implementation Strategy

The theme uses **CSS variable swapping** via `[data-theme='opsml'].theme-dark` — not Tailwind `dark:` prefixes. This means:

1. **Prefer theme-aware CSS variables** over hardcoded Tailwind colors
2. When a component uses `text-black`, the CSS variable system remaps it — but only if the component uses the themed token, not Tailwind's literal `text-black`
3. For components with hardcoded hex values or Tailwind gray classes, add explicit overrides in `app.css` under `.theme-dark` scope
4. Icon colors should use `currentColor` to inherit the phosphor green from their parent text color
