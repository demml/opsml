from __future__ import annotations

import argparse
import asyncio
import os

os.environ.setdefault("OPSML_TRACKING_URI", "http://localhost:8090")
os.environ.setdefault("SCOUTER_SERVER_URI", "http://localhost:8000")
os.environ.setdefault("SCOUTER_GRPC_URI", "http://localhost:50051")

from opsml.logging import LoggingConfig, RustyLogger

from .agents import build_runner, run_agent_turn, run_query
from .setup import AgentConfig, teardown

logger = RustyLogger.get_logger(LoggingConfig.default())


def run_queries(config: AgentConfig, queries: list[str]) -> list[str]:
    config.begin_run()
    responses: list[str] = []
    for query in queries:
        runner, session_service = build_runner(config)
        responses.append(
            asyncio.run(
                run_agent_turn(
                    runner,
                    session_service,
                    query=query,
                )
            )
        )
    return responses


async def run_queries_async(config: AgentConfig, queries: list[str]) -> list[str]:
    config.begin_run()
    responses: list[str] = []
    for query in queries:
        runner, session_service = build_runner(config)
        responses.append(
            await run_agent_turn(
                runner,
                session_service,
                query=query,
            )
        )
    return responses


def main() -> None:
    parser = argparse.ArgumentParser(description="Run E2E support agent.")
    parser.add_argument(
        "query",
        nargs="?",
        default="Help me plan a weeknight dinner with ingredients and steps.",
    )
    args = parser.parse_args()

    try:
        response = run_query(args.query)
        print(response)
    finally:
        teardown()


if __name__ == "__main__":
    main()
