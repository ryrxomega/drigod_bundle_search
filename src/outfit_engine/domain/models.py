from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from outfit_engine.domain import (
    AppearanceSignature,
    BodySignature,
    ColorLCh,
    FitProfile,
    GenderMarket,
    Pattern,
    Seasonality,
    SetCohesionPolicy,
)


@dataclass(slots=True)
class ItemAttributes:
    item_id: str
    source: str
    role: str
    slot: str
    category: Optional[str] = None
    formality: int = 1
    seasonality: list[Seasonality] = field(default_factory=list)
    color: Optional[ColorLCh] = None
    pattern: Optional[Pattern] = None
    material: Optional[str] = None
    style_tags: list[str] = field(default_factory=list)
    presentation_tags: list[str] = field(default_factory=list)
    fit_profile: Optional[FitProfile] = None
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
    intended_market: Optional[GenderMarket] = None
    group_id: Optional[str] = None
    set_role: Optional[str] = None
    coord_set_kind: Optional[str] = None
    set_cohesion_policy: Optional[SetCohesionPolicy] = None
    leather_family: Optional[str] = None
    metal_family: Optional[str] = None
    metal_finish: Optional[str] = None
    bag_material: Optional[str] = None


@dataclass(slots=True)
class WardrobeItem:
    user_id: str
    user_item_id: str
    attributes: ItemAttributes
    favorites_flag: bool = False
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(slots=True)
class CatalogItem:
    catalog_item_id: str
    attributes: ItemAttributes
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(slots=True)
class Profile:
    user_id: str
    baseline_dressiness: int
    default_occasion: str
    guardrails: dict[str, str] = field(default_factory=dict)
    style_signature: dict[str, str] = field(default_factory=dict)
    favorites: list[str] = field(default_factory=list)
    appearance_signature: Optional[AppearanceSignature] = None
    body_signature: Optional[BodySignature] = None


@dataclass(slots=True)
class ContextPolicy:
    target_formality_by_occasion: dict[str, tuple[int, int]]
    accessory_defaults_by_occasion: dict[str, list[str]]
    temperature_bands: dict[str, tuple[float, float]]


@dataclass(slots=True)
class RuleSet:
    ruleset_version: str
    layering_graph: dict[str, list[str]]
    coordinated_sets: dict[str, object]
    accessory_consistency: dict[str, object]
    weights: dict[str, float]
    skin_synergy: dict[str, object]
    body_proportion: dict[str, object]
    template_ranking: dict[str, list[str]]


@dataclass(slots=True)
class OutfitSlot:
    slot: str
    item_id: str
    source: str  # "wardrobe" or "catalog"


@dataclass(slots=True)
class Outfit:
    outfit_id: str
    user_id: str
    ruleset_version: str
    template_id: str
    slots: dict[str, list[OutfitSlot]]
    scores: dict[str, float]
    explanations: list[str]
    used_catalog_item: Optional[str] = None
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(slots=True)
class Feedback:
    feedback_id: str
    idempotency_key: str
    user_id: str
    outfit_id: str
    feedback_type: str
    reasons: list[str]
    rating: Optional[float] = None
    recorded_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
