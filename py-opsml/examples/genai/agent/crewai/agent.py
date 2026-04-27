from __future__ import annotations

import os
from typing import Any, Callable

from fastapi import FastAPI
from openinference.instrumentation.crewai import CrewAIInstrumentor
from opentelemetry.trace import get_tracer_provider
from pydantic import BaseModel
from opsml.scouter import trace
from opsml.scouter.evaluate import EvalRecord

from ..shared import get_shared_config, teardown

config = get_shared_config()
_crewai_instrumentor = CrewAIInstrumentor()
_crewai_instrumentor.instrument(skip_dep_check=True, tracer_provider=get_tracer_provider())

AgentCallback = Callable[[str, str], None]


class AgentRequest(BaseModel):
    query: str


class AgentResponse(BaseModel):
    response: str


def _emit_eval_record(query: str, response: str) -> None:
    tracer = trace.get_tracer("evaluate.agent.crewai")
    with tracer.start_as_current_span("crewai.callback") as span:
        span.add_queue_item(
            "interactive_support_agent",
            EvalRecord(
                id=f"crewai_interactive_{abs(hash((query, response))) % 1_000_000}",
                context={"query": query, "response": response},
            ),
        )


def _build_crew(query: str, callback: AgentCallback):
    from crewai import Agent, Crew, LLM, Task
    from crewai.tasks.task_output import TaskOutput

    llm = LLM(
        model="gemini/gemini-2.5-flash",
        api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0.0,
    )
    qa_agent = Agent(
        role="Interactive Support Assistant",
        goal="Provide practical iterative guidance.",
        backstory=config.prompt.prompt.message.text,
        llm=llm,
        verbose=False,
    )

    def on_task_complete(output: TaskOutput) -> None:
        callback(query, output.raw)

    task = Task(
        description=query,
        expected_output="Actionable next step.",
        agent=qa_agent,
    )
    return Crew(
        agents=[qa_agent],
        tasks=[task],
        tracing=True,
        verbose=False,
        task_callback=on_task_complete,
    )


def _fallback_response(query: str) -> str:
    lowered = query.lower()
    if "dinner" in lowered:
        return "Pick a protein, a vegetable, and a starch, then sequence prep to minimize total time."
    if "timeout" in lowered:
        return "Measure dependency latency, tune timeouts, and reduce retry storms."
    return "Fallback response because GOOGLE_API_KEY is not set."


def run_agent(query: str, callback: AgentCallback | None = None) -> str:
    on_response = callback or _emit_eval_record

    if not os.getenv("GOOGLE_API_KEY"):
        response = _fallback_response(query)
        on_response(query, response)
        return response

    from crewai.crews.crew_output import CrewOutput

    result: Any = _build_crew(query=query, callback=on_response).kickoff()
    if isinstance(result, CrewOutput):
        return result.raw
    return str(result)


app = FastAPI(title="OpsML CrewAI Interactive Agent")


@app.post("/ask", response_model=AgentResponse)
def ask(request: AgentRequest) -> AgentResponse:
    return AgentResponse(response=run_agent(request.query))


def shutdown() -> None:
    _crewai_instrumentor.uninstrument()
    teardown()


if __name__ == "__main__":
    import argparse

    _parser = argparse.ArgumentParser(description="Run CrewAI agent example.")
    _parser.add_argument("query", help="Query to send to the agent.")
    _args = _parser.parse_args()
    print(run_agent(_args.query))
    teardown()
