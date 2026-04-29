import importlib

import opsml
import opsml.scouter as scouter
import opsml.scouter.tracing as tracing_module


def test_scouter_service_map_is_lazy_loaded():
    reloaded = importlib.reload(scouter)
    assert "service_map" not in reloaded.__dict__

    service_map = reloaded.service_map
    assert service_map is not None
    assert "service_map" in reloaded.__dict__


def test_service_map_helpers_exposed_without_py_prefix():
    assert hasattr(opsml._opsml, "normalize_endpoint")
    assert hasattr(opsml._opsml, "extract_trace_id")
    assert hasattr(opsml._opsml, "infer_schema")
    assert not hasattr(opsml._opsml, "py_normalize_endpoint")
    assert not hasattr(opsml._opsml, "py_extract_trace_id")
    assert not hasattr(opsml._opsml, "py_infer_schema")


def test_scouter_submodule_import_smoke():
    from opsml.scouter import bifrost, evaluate, transport

    assert hasattr(bifrost, "Bifrost")
    assert hasattr(evaluate, "EvalOrchestrator")
    assert hasattr(transport, "GrpcConfig")


def test_get_tracer_falls_back_when_opentelemetry_missing(monkeypatch):
    class FakeBaseTracer:
        def __init__(self, name: str):
            self.name = name

    monkeypatch.setattr(tracing_module, "HAS_OPENTELEMETRY", False)
    monkeypatch.setattr(tracing_module, "BaseTracer", FakeBaseTracer)

    tracer = tracing_module.get_tracer("fallback-service")
    assert isinstance(tracer, tracing_module.ScouterTracer)
