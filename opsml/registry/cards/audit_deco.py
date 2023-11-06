from typing import Optional, Protocol, cast

from opsml.registry.cards.base import ArtifactCard
from opsml.registry.cards.types import CardType


class AuditCard(Protocol):
    @property
    def card_type(self) -> str:
        ...

    @property
    def uid(self) -> str:
        ...

    def add_card(self, card: ArtifactCard) -> None:
        ...


def add_to_auditcard(self, auditcard: Optional[AuditCard] = None, auditcard_uid: Optional[str] = None) -> None:
    """Add card uid to auditcard

    Args:
        auditcard:
            Optional AuditCard to add card uid to
        auditcard_uid:
            Optional uid of AuditCard to add card uid to

    """

    if self.uid is None:
        raise ValueError("Card must be registered before adding to auditcard")

    if auditcard_uid is not None:
        from opsml.registry.sql.registry import (  # pylint: disable=cyclic-import
            CardRegistry,
        )

        audit_registry = CardRegistry(registry_name="audit")
        loaded_card = cast(AuditCard, audit_registry.load_card(uid=auditcard_uid))
        loaded_card.add_card(card=self)
        audit_registry.update_card(card=loaded_card)  # type: ignore

        if self.card_type in [CardType.DATACARD, CardType.MODELCARD]:
            self.metadata.auditcard_uid = loaded_card.uid

        return None

    if auditcard is not None:
        return auditcard.add_card(card=self)

    return None


def auditable(cls_):
    setattr(cls_, "add_to_auditcard", add_to_auditcard)
    return cls_
