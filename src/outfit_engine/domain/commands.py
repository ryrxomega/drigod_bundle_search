from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional
from uuid import uuid4


def _default_id() -> str:
    return str(uuid4())


@dataclass
class Command:
    idempotency_key: str = field(default_factory=_default_id)
    schema_version: str = "v1"


@dataclass
class ColorDto:
    L: float
    C: float
    h: float


@dataclass
class PatternDto:
    type: Optional[str] = None
    scale: Optional[str] = None


@dataclass
class ItemDto:
    user_item_id: Optional[str] = None
    catalog_item_id: Optional[str] = None
    role: str = ""
    slot: str = ""
    category: Optional[str] = None
    formality: int = 3
    seasonality: list[str] = field(default_factory=list)
    color: Optional[ColorDto] = None
    pattern: Optional[PatternDto] = None
    material: Optional[str] = None
    style_tags: list[str] = field(default_factory=list)
    presentation_tags: list[str] = field(default_factory=list)
    fit_profile: Optional[str] = None
    top_length_class: Optional[str] = None
    bottom_rise_class: Optional[str] = None
    shoulder_structure: Optional[str] = None
    waist_emphasis: Optional[str] = None
    skirt_silhouette: Optional[str] = None
    pattern_orientation: Optional[str] = None
    leg_opening_cm: Optional[float] = None
    footwear_class: Optional[str] = None
    bag_kind: Optional[str] = None
    jewelry_kind: Optional[str] = None
    intended_market: Optional[str] = None
    group_id: Optional[str] = None
    set_role: Optional[str] = None
    coord_set_kind: Optional[str] = None
    set_cohesion_policy: Optional[str] = None
    leather_family: Optional[str] = None
    metal_family: Optional[str] = None
    metal_finish: Optional[str] = None
    bag_material: Optional[str] = None


@dataclass
class AddItem(Command):
    user_id: str = ""
    item: ItemDto = field(default_factory=ItemDto)


@dataclass
class UpdateItem(Command):
    user_id: str = ""
    user_item_id: str = ""
    patch: dict = field(default_factory=dict)


@dataclass
class RemoveItem(Command):
    user_id: str = ""
    user_item_id: str = ""


@dataclass
class AddCatalogItem(Command):
    item: ItemDto = field(default_factory=ItemDto)


@dataclass
class UpdateCatalogItem(Command):
    catalog_item_id: str = ""
    patch: dict = field(default_factory=dict)


@dataclass
class RemoveCatalogItem(Command):
    catalog_item_id: str = ""


@dataclass
class SetProfile(Command):
    user_id: str = ""
    baseline_dressiness: int = 3
    default_occasion: str = "casual_day"
    guardrails: dict = field(default_factory=dict)
    style_signature: dict = field(default_factory=dict)


@dataclass
class SetAppearanceProfile(Command):
    user_id: str = ""
    appearance_signature: dict = field(default_factory=dict)


@dataclass
class SetBodySignature(Command):
    user_id: str = ""
    body_signature: dict = field(default_factory=dict)


@dataclass
class GenerateOutfit(Command):
    user_id: str = ""
    mode: str = "ad_hoc"
    context: Optional[dict] = None
    allow_catalog: bool = False
    ruleset_version: Optional[str] = None
    determinism_key: Optional[str] = None


@dataclass
class ReplaceSlot(Command):
    user_id: str = ""
    outfit_id: str = ""
    target_slot: str = ""
    max_alternatives: int = 5
    determinism_key: Optional[str] = None


@dataclass
class RecordFeedback(Command):
    user_id: str = ""
    outfit_id: str = ""
    feedback_type: str = ""
    reasons: list[str] = field(default_factory=list)
    rating: Optional[float] = None
