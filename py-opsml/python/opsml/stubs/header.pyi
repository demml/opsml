# pylint: disable=redefined-builtin, invalid-name, dangerous-default-value, missing-final-newline, arguments-differ

import datetime
from pathlib import Path
from types import TracebackType
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Generic,
    Iterator,
    List,
    Literal,
    Mapping,
    Optional,
    ParamSpec,
    Protocol,
    Sequence,
    Tuple,
    Type,
    TypeAlias,
    Union,
    overload,
)

from typing_extensions import TypeVar

AttributeValue = Union[
    str,
    bool,
    int,
    float,
    Sequence[str],
    Sequence[bool],
    Sequence[int],
    Sequence[float],
]
Attributes = Optional[Mapping[str, AttributeValue]]

SerializedType: TypeAlias = Union[str, int, float, dict, list]
CardInterfaceType: TypeAlias = Union["DataInterface", "ModelInterface"]  # type: ignore[name-defined]
ServiceCardInterfaceType: TypeAlias = Dict[str, Union["DataInterface", "ModelInterface"]]  # type: ignore[name-defined]
LoadInterfaceType: TypeAlias = Union[ServiceCardInterfaceType, ServiceCardInterfaceType]
Context: TypeAlias = Union[Dict[str, Any], "BaseModel"]

P = ParamSpec("P")
R = TypeVar("R")

if TYPE_CHECKING:
    from opentelemetry.trace import SpanContext
else:
    class SpanContext:
        pass

class BaseModel(Protocol):
    """Protocol for pydantic BaseModel to ensure compatibility with context"""

    def model_dump(self) -> Dict[str, Any]:
        """Dump the model as a dictionary"""

    def model_dump_json(self) -> str:
        """Dump the model as a JSON string"""

    def __str__(self) -> str:
        """String representation of the model"""
