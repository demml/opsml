from enum import Enum
from pydantic import BaseModel, validator


class OnnxDataType(str, Enum):
    NUMPY_ARRAY = "NUMPY_ARRAY"
    PANDAS_DATAFRAME = "PANDAS_DATAFRAME"
    DICT = "DICT"


class LoadedApiModelDef(BaseModel):
    model_name: str
    model_type: str
    onnx_definition: bytes
    onnx_version: str
    input_signature: dict
    output_signature: dict
    model_version: str
    data_dict: dict
    sample_data: dict

    @validator("onnx_definition")
    def convert_to_bytes(cls, definition) -> bytes:  # pylint: disable = no-self-argument
        if isinstance(definition, str):
            return bytes.fromhex(definition)
        return definition
