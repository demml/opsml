from pathlib import Path
from opsml.service import OpsmlServiceSpec


def test_service_spec_load():
    file_path = Path(__file__).parent / "assets" / "agent_card.yaml"
    spec = OpsmlServiceSpec.from_path(file_path)
    print(spec)
    a
