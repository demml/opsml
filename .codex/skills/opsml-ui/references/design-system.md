# OpsML UI Design System

OpsML uses a loud, developer-facing neo-brutalist style. Preserve that visual identity unless the task explicitly asks for a redesign.

## Non-negotiables
- Use theme tokens from `opsml-theme.css` and `src/app.css`.
- Prefer `bg-surface-*`, `bg-primary-*`, `bg-secondary-*`, `bg-tertiary-*`, `bg-success-*`, `bg-warning-*`, `bg-error-*`.
- Use black borders or existing theme-border patterns.
- Use hard-offset shadows (`shadow`, `shadow-small`, `shadow-primary`) instead of soft shadows.
- Use fast transitions (`duration-100` to `duration-200`) and tactile press states (`shadow-click`, `shadow-click-small`).

Do not introduce:
- Arbitrary hex colors unless already present in repo-owned assets or theme definitions
- Blur-heavy or glassmorphism UI
- Gray-on-gray generic SaaS styling
- Large rounded radii beyond the current system defaults
- Soft shadow systems that fight the existing brutalist look

## Typography
- Sans font is Roboto
- Monospace font is JetBrains Mono
- `font-black` and uppercase tracking are used for labels, pills, and strong section headers
- Dense data areas should stay readable and restrained; save louder composition for heroes and empty states

## Where tokens come from
- `opsml-theme.css` defines color scales and theme variables
- `src/app.css` defines font, shadow, interaction, and utility patterns

## Styling rules by context
- Dense dashboards and tables:
  - favor clear structure, small shadows, restrained backgrounds
  - avoid rotations and decorative clutter
- Cards, pills, modals, and controls:
  - use visible borders, hard shadows, and clear affordances
- Empty states or top-level feature headers:
  - gradients and louder visual treatment are acceptable if they still feel like OpsML

## Reuse before inventing
Check existing components before designing new chrome:
- `src/lib/components/utils/`
- `src/lib/components/card/`
- `src/lib/components/scouter/`
- `src/lib/components/trace/`

If a new component is needed, match existing spacing, border, shadow, and token choices rather than introducing a parallel mini-design-system.
