import uvicorn
from fastapi import FastAPI
from google.adk.cli.fast_api import get_fast_api_app
from pathlib import Path
from prometheus_fastapi_instrumentator import Instrumentator

from .config import config


def create_web_app() -> FastAPI:
    """Serve your agent with the ADK web UI for local testing and deployment."""
    app = get_fast_api_app(
        agents_dir=str(Path(__file__).parent.parent),
        web=True,
        host=config.agent_url.host or "0.0.0.0",
        port=config.agent_url.port or 8002,
    )

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "healthy", "service": "goodbye-agent"}

    Instrumentator(excluded_handlers=["/health"]).instrument(app).expose(app)

    return app


app = create_web_app()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
