from pydantic import BaseModel


class HealthCheckResult(BaseModel):
    is_alive: bool
