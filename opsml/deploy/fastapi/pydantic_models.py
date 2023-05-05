from pydantic import BaseModel


class HealthCheck(BaseModel):
    is_alive: bool
