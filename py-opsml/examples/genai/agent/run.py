"""CLI runner for agent examples — no API server required.

Usage:
    python -m examples.genai.agent.run --backend openai "Help me plan dinner"
    python -m examples.genai.agent.run --backend google "My API times out"
    python -m examples.genai.agent.run --backend crewai "Debug this flaky test"

Run from py-opsml/:
    uv run python -m examples.genai.agent.run --backend openai "Help me plan dinner"
"""

from __future__ import annotations

import argparse
import asyncio
import sys

BACKENDS = ("openai", "google", "crewai")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run an agent example from the CLI.",
    )
    parser.add_argument(
        "--backend",
        choices=BACKENDS,
        required=True,
        help="Agent backend to use.",
    )
    parser.add_argument(
        "query",
        help="Query to send to the agent.",
    )
    return parser.parse_args()


def _run_openai(query: str) -> str:
    from .openai.agent import run_agent

    return run_agent(query)


async def _run_google(query: str) -> str:
    from .google.agent import build_agent_service

    service = build_agent_service()
    return await service.run(query)


def _run_crewai(query: str) -> str:
    from .crewai.agent import run_agent

    return run_agent(query)


def main() -> None:
    args = _parse_args()

    if args.backend == "openai":
        response = _run_openai(args.query)
    elif args.backend == "google":
        response = asyncio.run(_run_google(args.query))
    elif args.backend == "crewai":
        response = _run_crewai(args.query)
    else:
        print(f"Unknown backend: {args.backend}", file=sys.stderr)
        sys.exit(1)

    print(response)

    from .shared import teardown

    teardown()


if __name__ == "__main__":
    main()
