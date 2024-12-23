from opsml.data.interfaces._base import DataInterface
from opsml.types import AllowedDataType


class SqlData(DataInterface):
    """Arrow Table data interface

    Args:

        sql_logic:
            Dictionary of strings containing sql logic or sql files used to create the data
        feature_descriptions:
            Dictionary or feature descriptions
    """

    @property
    def data_type(self) -> str:
        return AllowedDataType.SQL.value

    @staticmethod
    def name() -> str:
        return SqlData.__name__
