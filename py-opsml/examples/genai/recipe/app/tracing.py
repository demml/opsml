from opsml.scouter import GrpcConfig
from opsml.scouter.tracing import get_tracer, init_tracer

init_tracer(
    service_name="agent-recipe-service",
    transport_config=GrpcConfig(),
)

tracer = get_tracer("agent-recipe-service")
