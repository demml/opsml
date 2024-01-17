import uvicorn
from core.config import Config
from core.lifespan_handler import lifespan
from core.routes import router
from fastapi import FastAPI


class OpsmlApp:
    """Initializes FastAPI app for opsml model serving"""

    def __init__(self, port: int = 8888):
        self.port = port
        self.app = FastAPI(title=Config.APP_NAME, version=Config.APP_VERSION, lifespan=lifespan)

    def run(self) -> None:
        """Run FastApi App"""
        self.app.include_router(router)
        uvicorn.run(self.app, host="0.0.0.0", port=self.port)


if __name__ == "__main__":
    OpsmlApp().run()
