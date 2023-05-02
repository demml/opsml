from enum import Enum
from pydantic import BaseModel, validator


class OnnxDataType(str, Enum):
    NUMPY_ARRAY = "NUMPY_ARRAY"
    PANDAS_DATAFRAME = "PANDAS_DATAFRAME"
    DICT = "DICT"
