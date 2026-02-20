from opsml.scouter.tracing import init_tracer, get_tracer
from opsml.scouter import GrpcConfig

init_tracer(
    service_name="agent-recipe-service",
    transport_config=GrpcConfig(),
)

tracer = get_tracer("agent-recipe-service")
