#### begin imports ####

from typing import Optional

#### end of imports ####

def py_normalize_endpoint(path: str) -> str:
    """Strip UUID and integer path segments to prevent cardinality explosion.

    ``/users/12345/orders`` → ``/users/{id}/orders``
    """

def py_extract_trace_id(traceparent: str) -> Optional[str]:
    """Extract the trace ID from a W3C ``traceparent`` header value.

    Returns ``None`` if the header is absent, malformed, or empty.
    """

def py_infer_schema(body: bytes) -> Optional[str]:
    """Inspect a JSON object body and return a JSON-encoded ``{field: type}`` map.

    Returns ``None`` if the body is not valid JSON or is not a top-level object.
    """

__all__ = [
    "py_extract_trace_id",
    "py_infer_schema",
    "py_normalize_endpoint",
]
