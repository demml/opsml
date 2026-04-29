# OpsML UI Working Map

Use this file to find the right feature area quickly before editing.

## Card browsing and card detail
- Listing routes: `src/routes/opsml/[registry]/...`
- Card detail routes: `src/routes/opsml/[registry]/card/[space]/[name]/[version]/...`
- Shared card UI: `src/lib/components/card/`
- Card server helpers: `src/lib/server/card/`

## Agent and prompt workflows
- Agent routes: `src/routes/opsml/agent/...`
- Agent UI: `src/lib/components/card/agent/`
- Prompt UI: `src/lib/components/card/prompt/`
- Agent eval and playground code lives with those feature components

## Monitoring and Scouter
- Monitoring pages under card detail routes:
  - `monitoring/psi`
  - `monitoring/spc`
  - `monitoring/custom`
- Monitoring UI: `src/lib/components/scouter/`
- Server helpers: `src/lib/server/scouter/`
- Internal API proxies: `src/routes/api/scouter/...`

## Observability and traces
- Top-level observability route: `src/routes/opsml/observability/`
- Card-level observability route: card detail `observability/`
- Trace UI: `src/lib/components/trace/`
- Trace server helpers: `src/lib/server/trace/`
- Internal API proxies: `src/routes/api/scouter/observability/...`

## Files and README
- File routes under card detail `files/`
- File UI: `src/lib/components/files/`
- README UI: `src/lib/components/readme/`
- Server helpers: `src/lib/server/card/files/` and `src/lib/server/card/readme/`

## Home, space, user, nav
- Home: `src/lib/components/home/` and `src/routes/opsml/home/`
- Space: `src/lib/components/space/` and `src/routes/opsml/space/`
- User: `src/lib/components/user/` and `src/routes/opsml/user/`
- Navigation shell: `src/lib/components/nav/`

## Shared infrastructure
- Route constants: `src/lib/components/api/routes.ts`
- Shared UI settings or stores: `src/lib/components/settings/`
- Utility components: `src/lib/components/utils/`
- Charts and generic viz: `src/lib/components/viz/`

## Good first files to inspect
- Theme or styling change:
  - `opsml-theme.css`
  - `src/app.css`
  - the feature component using the styles
- New page or route behavior:
  - the route folder under `src/routes/opsml/...`
  - matching components under `src/lib/components/...`
- New backend-backed UI behavior:
  - `src/lib/components/api/routes.ts`
  - `src/lib/server/...`
  - `src/routes/api/...`
