from __future__ import annotations

import argparse
import asyncio
import os

os.environ.setdefault("OPSML_TRACKING_URI", "http://localhost:8090")
os.environ.setdefault("SCOUTER_SERVER_URI", "http://localhost:8000")
os.environ.setdefault("SCOUTER_GRPC_URI", "http://localhost:50051")

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from .agents import run_agent_turn
from .agents.triage import build_triage_agent
from .setup import APP_NAME, get_agent_config, teardown


def run_single_agent_query(query: str) -> str:
    config = get_agent_config()
    config.begin_run()
    session_service = InMemorySessionService()
    runner = Runner(
        agent=build_triage_agent(config),
        app_name=APP_NAME,
        session_service=session_service,
    )
    return asyncio.run(run_agent_turn(runner, session_service, query=query))


def main() -> None:
    parser = argparse.ArgumentParser(description="Run one online single-agent request.")
    parser.add_argument(
        "query",
        nargs="?",
        default="Classify this request: I need a quick dinner plan for tonight.",
    )
    args = parser.parse_args()

    try:
        response = run_single_agent_query(args.query)
        print(response)
    finally:
        teardown()


if __name__ == "__main__":
    main()
