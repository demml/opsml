# Theming

## Table Of Contents

- Source files to inspect
- Tailwind v4 and Skeleton
- Token usage
- Dark mode
- Component class patterns
- Icons and charts
- Anti-patterns
- Official references

## Source Files To Inspect

- `crates/opsml_server/opsml_ui/src/app.css`
- `crates/opsml_server/opsml_ui/opsml-theme.css`
- `crates/opsml_server/opsml_ui/DARK_MODE_STYLE_GUIDE.md`
- `crates/opsml_server/opsml_ui/src/routes/+layout.svelte`
- `crates/opsml_server/opsml_ui/src/lib/components/nav/Navbar.svelte`
- `crates/opsml_server/opsml_ui/src/lib/components/nav/Sidebar.svelte`
- `crates/opsml_server/opsml_ui/src/lib/components/settings/theme.svelte.ts`

## Tailwind V4 And Skeleton

OpsML uses Tailwind v4's CSS-first setup:

- `@import 'tailwindcss'`
- `@plugin '@tailwindcss/forms'`
- `@plugin '@tailwindcss/typography'`
- `@import '@skeletonlabs/skeleton'`
- `@import '@skeletonlabs/skeleton/optional/presets'`
- `@import "../opsml-theme.css"`
- `@source '../node_modules/@skeletonlabs/skeleton-svelte/dist'`
- `@theme` for local tokens and utilities

Use Skeleton/Skeleton Svelte for primitives already present in the app, including toast provider, modals/dialogs, switches, menus, tabs, and combobox-like controls. Do not introduce a second component system.

## Token Usage

Prefer theme-aware classes:

- Surfaces: `bg-surface-*`
- Brand and state: `bg-primary-*`, `text-primary-*`, `bg-secondary-*`, semantic state classes when functional
- Borders: `border`, `border-black`, `border-primary-*`, `border-surface-*` where resolved through the theme
- Elevation: `shadow`, `shadow-small`, `shadow-primary`, `shadow-hover`, `shadow-hover-small`, `shadow-click`
- Text: `text-black`, `text-primary-*`, `text-secondary-*`, semantic text for functional warnings and errors

Use local utilities from `app.css` before creating new one-off class recipes.

## Dark Mode

Dark mode is a phosphor terminal theme, not normal dark gray UI.

Rules:

- Use monochrome green-on-black surfaces and text from theme tokens.
- Use thin green-tinted borders and low-contrast dividers.
- Avoid hard offset shadows in dark mode. Use the dark-mode shadow tokens or no elevation.
- Avoid default gray text and near-white text in dark mode.
- Keep decorative accents monochrome. Use warning/error/success colors only for functional states.
- Icons should usually inherit `currentColor`.
- Dense tables, trace rows, file views, and dashboards must stay legible at compact sizes.

Light mode can keep OpsML's brutalist character, but components must survive dark-mode token resolution.

## Component Class Patterns

For compact buttons:

```svelte
<button
  type="button"
  class="rounded-base border-2 border-black bg-surface-50 px-3 py-2 text-sm font-bold text-primary-800 shadow-small shadow-hover-small"
>
  Refresh
</button>
```

For selected rows or navigation items:

```svelte
class={active
  ? "bg-primary-50 text-primary-800 border-primary-200"
  : "bg-surface-50 text-black border-transparent hover:bg-surface-100"}
```

For dense panels:

```svelte
<section class="rounded-base border-2 border-black bg-surface-50 shadow overflow-hidden">
  <header class="border-b-2 border-black px-3 py-2 text-sm font-bold text-primary-800">
    Trace Summary
  </header>
  <div class="p-3">
    ...
  </div>
</section>
```

Use these as patterns, not fixed recipes. Check the local component you are touching.

## Icons And Charts

- Prefer `lucide-svelte` for tool and navigation icons.
- Icon-only buttons need labels.
- Chart colors should come from theme or chart utility functions, not hardcoded palettes.
- Recreate or update charts when theme mode changes.

## Anti-Patterns

- Hardcoded color palettes as the default recommendation.
- Arbitrary shadow utilities as examples.
- Separate CSS systems that bypass `app.css` and `opsml-theme.css`.
- Decorative multicolor gradients in operational views.
- Styling only for light mode.
- Using Skeleton defaults without checking OpsML token resolution and dark-mode behavior.

## Official References

- Tailwind directives: https://tailwindcss.com/docs/functions-and-directives
- Tailwind theme variables: https://tailwindcss.com/docs/theme
- Skeleton v4: https://v4.skeleton.dev/
