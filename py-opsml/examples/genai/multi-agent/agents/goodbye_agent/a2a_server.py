import uvicorn
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from prometheus_fastapi_instrumentator import Instrumentator
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse

from .agent import create_agent
from .config import config
from .lifespan import get_app_state, lifespan


def create_app() -> Starlette:
    """Serve your agent over the A2A protocol."""
    _, _, agent_spec = get_app_state()

    skills_list = [
        AgentSkill(
            id=skill.id,
            name=skill.name,
            description=skill.description,
            tags=skill.tags,
            input_modes=skill.input_modes,
            output_modes=skill.output_modes,
            examples=skill.examples,
        )
        for skill in agent_spec.skills
    ]

    agent_card = AgentCard(
        name=agent_spec.name,
        url=config.agent_url.unicode_string(),
        description=agent_spec.description,
        version=agent_spec.version,
        capabilities=AgentCapabilities(),
        skills=skills_list,
        default_input_modes=agent_spec.default_input_modes,
        default_output_modes=agent_spec.default_output_modes,
        supports_authenticated_extended_card=agent_spec.capabilities.extended_agent_card,
    )

    app = to_a2a(
        agent=create_agent(),
        host=config.agent_url.host or "localhost",
        port=config.agent_url.port or 8002,
        agent_card=agent_card,
        lifespan=lifespan,
        # TODO-ESPRESSO: Production application need memory-backed storage implementations.
        # runner=...,
    )

    @app.route("/health", methods=["GET"])
    async def health_check(request: Request) -> JSONResponse:
        return JSONResponse(
            {
                "status": "healthy",
                "agent": agent_spec.name,
                "version": agent_spec.version,
            }
        )

    Instrumentator(excluded_handlers=["/health"]).instrument(app).expose(app)

    return app


if __name__ == "__main__":
    port = config.agent_url.port or 8002
    uvicorn.run(create_app(), host="0.0.0.0", port=port)
