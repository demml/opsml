from pydantic import BaseModel
import sqlalchemy


class BaseSQLConnection(BaseModel):
    """Base Connection model that all connections inherit from"""

    class Config:
        arbitrary_types_allowed = True
        extra = "allow"

    def _set_sqlalchemy_url(self):
        raise NotImplementedError

    def get_engine(self) -> sqlalchemy.engine.base.Engine:
        raise NotImplementedError
