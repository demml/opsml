# Agent-Friendly OpsML Work

OpsML is being shaped for both human developers and coding agents. The key direction is harness engineering: give agents strong guides before they act and strong sensors after they act.

## Design For Agents And Humans

Code should be readable by humans first and stable enough for agents to modify safely:
- Keep names domain-specific and unambiguous.
- Keep functions small enough that invariants are visible.
- Prefer typed contracts over loose dictionaries or stringly-typed conventions.
- Surface failures with stable codes, fields, hints, and docs where the repo supports them.
- Keep side effects at clear boundaries.

## Same Envelope Principle

Harness work should converge on the same structured shape across layers:
- HTTP responses.
- PyO3 exceptions.
- CLI output.
- `card.validate()`.
- `opsml lint`.
- Integrity checks.
- Eval results.

Use fields such as:
- `code`
- `field`
- `hint` or `suggested_action`
- `doc_url`
- `retry`

Agents should not need to parse paragraphs to understand what field to fix.

## Validation And Sensors

When adding governance behavior, think in layers:
- Edit-time or local lint sensors.
- Rust-native validation on core types.
- Registry/server chokepoints.
- Post-hoc integrity checks.
- Behavior evals for prompts and agents.

The Rust core should own validations that define durable OpsML correctness. Python should expose them ergonomically and test them as user workflows.

## Documentation Near APIs

Public Rust and Python APIs should include useful docs when they define:
- User-visible behavior.
- Required invariants.
- Error conditions.
- Security constraints.
- Serialization formats.
- Cross-language boundary behavior.

Do not add noisy comments that restate simple code. Add concise comments when they preserve hard-won context, such as why a Python lifetime is intentionally kept at the boundary.
