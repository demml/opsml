# pylint: disable=invalid-name
from contextlib import asynccontextmanager
from pathlib import Path
from opsml.scouter.queue import GenAIEvalRecord
from opsml.card import PromptCard
from fastapi import FastAPI, Request
from opsml.app import AppState
from opsml.scouter import GrpcConfig
from opsml.scouter.tracing import shutdown_tracer
from pydantic import BaseModel
from app.tracing import tracer
from app.models import Recipe
from pydantic_ai import Agent


class Question(BaseModel):
    question: str


response_agent = Agent(
    name="recipe_agent",
    model="google-gla:gemini-2.5-flash-lite",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app_state = AppState.from_path(
        path=Path("app/service_artifacts"),
        transport_config=GrpcConfig(),
    )
    tracer.set_scouter_queue(app_state.queue)
    app.state.agent_helper = response_agent
    app.state.app_state = app_state
    app.state.recipe_prompt = app_state.service["recipe"]

    yield

    shutdown_tracer()
    app.state.app_state = None
    app.state.agent_helper = None


app = FastAPI(lifespan=lifespan)


@app.post("/predict", response_model=Recipe)
async def predict(request: Request, payload: Question) -> Recipe:
    # Grab the reformulated prompt and response prompt from the app state
    with tracer.start_as_current_span(name="predict_endpoint") as span:
        recipe_prompt: PromptCard = request.app.state.recipe_prompt

        parameterized_query = recipe_prompt.prompt.bind(
            user_request=payload.question
        ).messages[0]

        agent_helper: Agent = request.app.state.agent_helper
        response = await agent_helper.run(
            user_prompt="give me a meatball recipe",
            output_type=Recipe,
        )

        recipe = response.output

        span.add_queue_item(
            alias="recipe_metrics",
            item=GenAIEvalRecord(context={"recipe": recipe}),
        )

        return recipe
