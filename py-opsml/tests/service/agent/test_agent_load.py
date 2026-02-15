from pathlib import Path
from opsml.service import OpsmlServiceSpec


def test_service_spec_load():
    """This test loads and verifies the agent card spec yaml file for correctness and compatibility with the OpsmlServiceSpec dataclass."""
    file_path = Path(__file__).parent / "assets1" / "agent_card.yaml"
    _spec = OpsmlServiceSpec.from_path(file_path)


def test_service_spec_load_paths():
    """This test loads an opsml spec that references agent cards with relative paths, verifying that path resolution works correctly."""
    file_path = Path(__file__).parent / "assets2" / "opsml_spec.yaml"
    _spec = OpsmlServiceSpec.from_path(file_path)
