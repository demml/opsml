# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

@AGENTS.md

## Claude Code Notes

- After modifying any Rust type exposed to Python, run the `pyo3-checklist` skill to verify all 6 wiring layers are complete (Rust impl → re-export → PyO3 registration → `__init__.py` → `__all__` → `.pyi` stub).
- Use the `rust-python` skill when working with PyO3 bindings or the Rust↔Python boundary.
- Use the `opsml-ui` skill when building, editing, or designing any UI component, page, layout, or dashboard.
- Use the `opsml-ts-svelte` skill when writing TypeScript logic, Svelte 5 components, or SvelteKit routing/data loading.
- Use the `agentic-architect` skill when modifying GenAI features, LLM client code, tool-calling logic, or anything in `opsml-mcp` / `opsml-genai`.
- Run the `pre-pr` skill before creating any pull request.
- Run the `review` skill for a full parallel code review (security, style, bugs, frontend) before merging.
