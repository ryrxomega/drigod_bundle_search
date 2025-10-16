from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4


@dataclass(slots=True)
class DomainEvent:
    event_id: str = field(default_factory=lambda: str(uuid4()))
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    schema_version: str = "v1"


@dataclass(slots=True)
class ItemAdded(DomainEvent):
    user_id: str = ""
    user_item_id: str = ""
    role: str = ""
    attributes_hash: str = ""


@dataclass(slots=True)
class ItemUpdated(DomainEvent):
    user_id: str = ""
    user_item_id: str = ""
    role: str = ""
    attributes_hash: str = ""
    changed_fields: list[str] = field(default_factory=list)


@dataclass(slots=True)
class ItemRemoved(DomainEvent):
    user_id: str = ""
    user_item_id: str = ""


@dataclass(slots=True)
class CatalogItemAdded(DomainEvent):
    catalog_item_id: str = ""
    role: str = ""
    attributes_hash: str = ""


@dataclass(slots=True)
class CatalogItemUpdated(DomainEvent):
    catalog_item_id: str = ""
    role: str = ""
    attributes_hash: str = ""
    changed_fields: list[str] = field(default_factory=list)


@dataclass(slots=True)
class CatalogItemRemoved(DomainEvent):
    catalog_item_id: str = ""


@dataclass(slots=True)
class ProfileUpdated(DomainEvent):
    user_id: str = ""
    changed_fields: list[str] = field(default_factory=list)


@dataclass(slots=True)
class AppearanceProfileUpdated(DomainEvent):
    user_id: str = ""
    changed_fields: list[str] = field(default_factory=list)


@dataclass(slots=True)
class BodySignatureUpdated(DomainEvent):
    user_id: str = ""
    changed_fields: list[str] = field(default_factory=list)


@dataclass(slots=True)
class RuleSetPublished(DomainEvent):
    ruleset_version: str = ""
    checksum: str = ""


@dataclass(slots=True)
class OutfitGenerated(DomainEvent):
    user_id: str = ""
    outfit_id: str = ""
    ruleset_version: str = ""
    template_id: str = ""
    context_applied: dict[str, Any] = field(default_factory=dict)
    used_catalog_item: Optional[str] = None
    quality_score: float = 0.0
    hard_constraint_passed: bool = True


@dataclass(slots=True)
class SlotReplaced(DomainEvent):
    user_id: str = ""
    outfit_id: str = ""
    target_slot: str = ""
    candidate_ids: list[str] = field(default_factory=list)
    hard_constraint_passed: bool = True


@dataclass(slots=True)
class FeedbackRecorded(DomainEvent):
    user_id: str = ""
    outfit_id: str = ""
    feedback_type: str = ""
    reasons: list[str] = field(default_factory=list)
    rating: Optional[float] = None
