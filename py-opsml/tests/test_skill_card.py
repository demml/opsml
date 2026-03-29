import tempfile
from pathlib import Path

import pytest
from opsml import AgentSkillStandard, DependencyKind, SkillCard, SkillDependency
from opsml.card import CardRegistry, RegistryType


def test_skillcard_creation():
    skill = AgentSkillStandard(
        name="test-skill",
        description="A test skill",
        body="## Instructions\n\nDo something useful.",
    )
    card = SkillCard(
        skill=skill,
        space="test-space",
        name="test-skill",
        tags=["test"],
        compatible_tools=["claude-code"],
    )
    assert card.name == "test-skill"
    assert card.space == "test-space"
    assert card.tags == ["test"]
    assert card.compatible_tools == ["claude-code"]
    assert card.skill.name == "test-skill"


def test_skillcard_dependency():
    dep = SkillDependency(name="other-skill", space="my-space", kind=DependencyKind.Skill)
    assert dep.name == "other-skill"
    assert dep.space == "my-space"

    dep2 = SkillDependency(
        name="my-mcp",
        space="tools",
        kind=DependencyKind.McpServer,
        version_req="^1.0.0",
    )
    assert dep2.version_req == "^1.0.0"


def test_skillcard_markdown_roundtrip():
    skill = AgentSkillStandard(
        name="my-skill",
        description="Does something helpful.",
        body="## Usage\n\nUse me.",
    )
    card = SkillCard(
        skill=skill,
        space="test",
        name="my-skill",
    )
    md = card.to_markdown()
    assert "my-skill" in md
    assert "Does something helpful." in md

    with tempfile.NamedTemporaryFile(suffix=".md", mode="w", delete=False) as f:
        f.write(md)
        tmp_path = Path(f.name)

    try:
        restored = SkillCard.from_markdown(tmp_path)
        assert restored.skill.name == "my-skill"
        assert restored.skill.description == "Does something helpful."
    finally:
        tmp_path.unlink(missing_ok=True)


def test_skillcard_registry_roundtrip(mock_db):
    skill = AgentSkillStandard(
        name="my-skill",
        description="Does something.",
        body="## Usage\n\nUse me.",
    )
    card = SkillCard(
        skill=skill,
        space="test",
        name="my-skill",
        tags=["test-tag"],
    )
    registry: CardRegistry[SkillCard] = CardRegistry(RegistryType.Skill)
    registry.register_card(card)

    assert card.uid is not None
    assert card.version is not None

    loaded: SkillCard = registry.load_card(uid=card.uid)
    assert loaded.name == card.name
    assert loaded.space == card.space
    assert loaded.skill.name == "my-skill"
    assert loaded.skill.description == "Does something."
