from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, Tuple
from uuid import uuid4

from outfit_engine.domain.commands import (
    AddCatalogItem,
    AddItem,
    GenerateOutfit,
    RecordFeedback,
    RemoveCatalogItem,
    RemoveItem,
    ReplaceSlot,
    SetAppearanceProfile,
    SetBodySignature,
    SetProfile,
    UpdateCatalogItem,
    UpdateItem,
)
from outfit_engine.domain.models import (
    CatalogItem,
    ContextPolicy,
    Feedback,
    ItemAttributes,
    Profile,
    RuleSet,
    WardrobeItem,
)
from outfit_engine.domain.value_objects import (
    AppearanceSignature,
    BodySignature,
    ColorLCh,
    FitPreference,
    FitProfile,
    HeightClass,
    Pattern,
    Seasonality,
    SetCohesionPolicy,
    ShoulderToHipRatio,
    SynergyStyle,
    TorsoLegRatio,
    Undertone,
    WaistDefinition,
)
from outfit_engine.infrastructure.repositories import (
    CatalogRepository,
    FeedbackRepository,
    OutfitRepository,
    ProfileRepository,
    SearchIndex,
    WardrobeRepository,
    attributes_hash,
)
from outfit_engine.services.recommendation_service import RecommendationService


class CommandHandler:
    def __init__(
        self,
        wardrobe_repo: WardrobeRepository,
        catalog_repo: CatalogRepository,
        profile_repo: ProfileRepository,
        outfit_repo: OutfitRepository,
        feedback_repo: FeedbackRepository,
        search_index: SearchIndex,
        recommendation_service: RecommendationService,
        ruleset: RuleSet,
        context_policy: ContextPolicy,
    ):
        self.wardrobe_repo = wardrobe_repo
        self.catalog_repo = catalog_repo
        self.profile_repo = profile_repo
        self.outfit_repo = outfit_repo
        self.feedback_repo = feedback_repo
        self.search_index = search_index
        self.recommendation_service = recommendation_service
        self.ruleset = ruleset
        self.context_policy = context_policy
        self.idempotency_store: Dict[str, Tuple[str, datetime]] = {}

    def handle_add_item(self, command: AddItem) -> dict:
        if command.idempotency_key in self.idempotency_store:
            return {"status": "ok"}

        user_item_id = command.item.user_item_id or str(uuid4())
        attributes = self._item_attributes_from_dto(
            command.item, item_id=user_item_id, source="wardrobe"
        )
        item = WardrobeItem(
            user_id=command.user_id,
            user_item_id=user_item_id,
            attributes=attributes,
        )

        self.wardrobe_repo.add_item(item)

        self.search_index.upsert_doc(
            scope=command.user_id,
            doc_id=item.user_item_id,
            document=self._build_search_document(item),
        )

        self.idempotency_store[command.idempotency_key] = (
            item.user_item_id,
            datetime.now(timezone.utc),
        )

        return {"status": "ok", "user_item_id": item.user_item_id}

    def handle_update_item(self, command: UpdateItem) -> dict:
        item = self.wardrobe_repo.get_item(command.user_id, command.user_item_id)
        if not item:
            raise ValueError("Item not found")

        for key, value in command.patch.items():
            if hasattr(item.attributes, key):
                setattr(item.attributes, key, value)

        self.wardrobe_repo.update_item(item)

        self.search_index.upsert_doc(
            scope=command.user_id,
            doc_id=command.user_item_id,
            document=self._build_search_document(item),
        )

        return {"status": "ok"}

    def handle_remove_item(self, command: RemoveItem) -> dict:
        self.wardrobe_repo.remove_item(command.user_id, command.user_item_id)
        self.search_index.remove_doc(command.user_id, command.user_item_id)

        return {"status": "ok"}

    def handle_add_catalog_item(self, command: AddCatalogItem) -> dict:
        catalog_item_id = command.item.catalog_item_id or str(uuid4())
        attributes = self._item_attributes_from_dto(
            command.item, item_id=catalog_item_id, source="catalog"
        )
        item = CatalogItem(
            catalog_item_id=catalog_item_id,
            attributes=attributes,
        )

        self.catalog_repo.add_item(item)

        self.search_index.upsert_doc(
            scope="catalog",
            doc_id=item.catalog_item_id,
            document=self._build_catalog_search_document(item),
        )

        return {"status": "ok", "catalog_item_id": item.catalog_item_id}

    def handle_update_catalog_item(self, command: UpdateCatalogItem) -> dict:
        item = self.catalog_repo.get_item(command.catalog_item_id)
        if not item:
            raise ValueError("Catalog item not found")

        for key, value in command.patch.items():
            if hasattr(item.attributes, key):
                setattr(item.attributes, key, value)

        self.catalog_repo.update_item(item)

        self.search_index.upsert_doc(
            scope="catalog",
            doc_id=command.catalog_item_id,
            document=self._build_catalog_search_document(item),
        )

        return {"status": "ok"}

    def handle_remove_catalog_item(self, command: RemoveCatalogItem) -> dict:
        self.catalog_repo.remove_item(command.catalog_item_id)
        self.search_index.remove_doc("catalog", command.catalog_item_id)

        return {"status": "ok"}

    def handle_set_profile(self, command: SetProfile) -> dict:
        profile = self.profile_repo.get(command.user_id)

        if not profile:
            profile = Profile(
                user_id=command.user_id,
                baseline_dressiness=command.baseline_dressiness,
                default_occasion=command.default_occasion,
                guardrails=command.guardrails,
                style_signature=command.style_signature,
            )
        else:
            profile.baseline_dressiness = command.baseline_dressiness
            profile.default_occasion = command.default_occasion
            profile.guardrails = command.guardrails
            profile.style_signature = command.style_signature

        self.profile_repo.save(profile)

        return {"status": "ok"}

    def handle_set_appearance_profile(self, command: SetAppearanceProfile) -> dict:
        profile = self.profile_repo.get(command.user_id)

        if not profile:
            profile = Profile(
                user_id=command.user_id,
                baseline_dressiness=3,
                default_occasion="casual_day",
            )

        appearance = command.appearance_signature
        profile.appearance_signature = AppearanceSignature(
            skin_lch=ColorLCh(**appearance["skin_lch"]) if appearance.get("skin_lch") else None,
            undertone=Undertone(appearance["undertone"]) if appearance.get("undertone") else None,
            hair_lch=ColorLCh(**appearance["hair_lch"]) if appearance.get("hair_lch") else None,
            eye_lch=ColorLCh(**appearance["eye_lch"]) if appearance.get("eye_lch") else None,
            synergy_style=SynergyStyle(appearance["synergy_style"])
            if appearance.get("synergy_style")
            else None,
        )

        self.profile_repo.save(profile)

        return {"status": "ok"}

    def handle_set_body_signature(self, command: SetBodySignature) -> dict:
        profile = self.profile_repo.get(command.user_id)

        if not profile:
            profile = Profile(
                user_id=command.user_id,
                baseline_dressiness=3,
                default_occasion="casual_day",
            )

        body = command.body_signature
        profile.body_signature = BodySignature(
            height_class=HeightClass(body["height_class"]) if body.get("height_class") else None,
            torso_leg_ratio=TorsoLegRatio(body["torso_leg_ratio"]) if body.get("torso_leg_ratio") else None,
            shoulder_to_hip_ratio=ShoulderToHipRatio(body["shoulder_to_hip_ratio"])
            if body.get("shoulder_to_hip_ratio")
            else None,
            waist_definition=WaistDefinition(body["waist_definition"])
            if body.get("waist_definition")
            else None,
            fit_pref=FitPreference(body["fit_pref"]) if body.get("fit_pref") else None,
            notes=body.get("notes", []),
        )

        self.profile_repo.save(profile)

        return {"status": "ok"}

    def handle_generate_outfit(self, command: GenerateOutfit) -> dict:
        outfit, event = self.recommendation_service.generate_outfit(
            user_id=command.user_id,
            context=command.context,
            allow_catalog=command.allow_catalog,
            ruleset_version=command.ruleset_version or self.ruleset.ruleset_version,
            determinism_key=command.determinism_key,
        )

        return {
            "outfit_id": outfit.outfit_id,
            "ruleset_version": outfit.ruleset_version,
            "template_id": outfit.template_id,
            "context_applied": event.context_applied,
            "used_catalog_item": outfit.used_catalog_item,
            "slots": {
                slot.slot: [
                    {
                        "id": slot.item_id,
                    }
                ]
                for slot in outfit.slots["items"]
            },
            "scores": outfit.scores,
            "explanations": outfit.explanations,
        }

    def handle_replace_slot(self, command: ReplaceSlot) -> dict:
        alternatives, cascade_plan, event = self.recommendation_service.replace_slot(
            user_id=command.user_id,
            outfit_id=command.outfit_id,
            target_slot=command.target_slot,
            max_alternatives=command.max_alternatives,
            determinism_key=command.determinism_key,
        )

        response = {"alternatives": alternatives}
        if cascade_plan:
            response["cascade_plan"] = cascade_plan

        return response

    def handle_record_feedback(self, command: RecordFeedback) -> dict:
        feedback = Feedback(
            feedback_id=str(uuid4()),
            idempotency_key=command.idempotency_key,
            user_id=command.user_id,
            outfit_id=command.outfit_id,
            feedback_type=command.feedback_type,
            reasons=command.reasons,
            rating=command.rating,
        )

        self.feedback_repo.save(feedback)

        return {"status": "ok"}

    def _item_attributes_from_dto(self, dto, *, item_id: str, source: str) -> ItemAttributes:
        color = None
        if dto.color:
            color = ColorLCh(L=dto.color.L, C=dto.color.C, h=dto.color.h)

        pattern = None
        if dto.pattern:
            pattern = Pattern(type=dto.pattern.type, scale=dto.pattern.scale)

        seasonality = [Seasonality(s) for s in dto.seasonality] if dto.seasonality else []

        set_cohesion_policy = (
            SetCohesionPolicy(dto.set_cohesion_policy)
            if dto.set_cohesion_policy
            else None
        )

        return ItemAttributes(
            item_id=item_id,
            source=source,
            role=dto.role,
            slot=dto.slot,
            category=dto.category,
            formality=dto.formality,
            seasonality=seasonality,
            color=color,
            pattern=pattern,
            material=dto.material,
            style_tags=dto.style_tags,
            presentation_tags=dto.presentation_tags,
            fit_profile=FitProfile(dto.fit_profile) if dto.fit_profile else None,
            top_length_class=dto.top_length_class,
            bottom_rise_class=dto.bottom_rise_class,
            shoulder_structure=dto.shoulder_structure,
            waist_emphasis=dto.waist_emphasis,
            skirt_silhouette=dto.skirt_silhouette,
            pattern_orientation=dto.pattern_orientation,
            leg_opening_cm=dto.leg_opening_cm,
            footwear_class=dto.footwear_class,
            bag_kind=dto.bag_kind,
            jewelry_kind=dto.jewelry_kind,
            intended_market=dto.intended_market,
            group_id=dto.group_id,
            set_role=dto.set_role,
            coord_set_kind=dto.coord_set_kind,
            set_cohesion_policy=set_cohesion_policy,
            leather_family=dto.leather_family,
            metal_family=dto.metal_family,
            metal_finish=dto.metal_finish,
            bag_material=dto.bag_material,
        )

    def _build_search_document(self, item: WardrobeItem) -> dict:
        attrs = item.attributes
        return {
            "id": item.user_item_id,
            "scope": item.user_id,
            "source": "wardrobe",
            "role": attrs.role,
            "slot": attrs.slot,
            "category": attrs.category,
            "formality": attrs.formality,
            "seasonality": [s.value for s in attrs.seasonality],
            "color": attrs.color.__dict__ if attrs.color else None,
            "pattern": attrs.pattern.__dict__ if attrs.pattern else None,
            "material": attrs.material,
            "style_tags": attrs.style_tags,
            "group_id": attrs.group_id,
            "set_role": attrs.set_role,
            "coord_set_kind": attrs.coord_set_kind,
            "set_cohesion_policy": attrs.set_cohesion_policy.value
            if attrs.set_cohesion_policy
            else None,
            "fit_profile": attrs.fit_profile.value if attrs.fit_profile else None,
            "top_length_class": attrs.top_length_class,
            "bottom_rise_class": attrs.bottom_rise_class,
            "shoulder_structure": attrs.shoulder_structure,
            "waist_emphasis": attrs.waist_emphasis,
            "skirt_silhouette": attrs.skirt_silhouette,
            "pattern_orientation": attrs.pattern_orientation,
            "leg_opening_cm": attrs.leg_opening_cm,
            "footwear_class": attrs.footwear_class,
            "bag_kind": attrs.bag_kind,
            "jewelry_kind": attrs.jewelry_kind,
            "leather_family": attrs.leather_family,
            "metal_family": attrs.metal_family,
            "metal_finish": attrs.metal_finish,
            "bag_material": attrs.bag_material,
            "updated_at": datetime.now(timezone.utc).timestamp(),
        }

    def _build_catalog_search_document(self, item: CatalogItem) -> dict:
        attrs = item.attributes
        return {
            "id": item.catalog_item_id,
            "scope": "catalog",
            "source": "catalog",
            "role": attrs.role,
            "slot": attrs.slot,
            "category": attrs.category,
            "formality": attrs.formality,
            "seasonality": [s.value for s in attrs.seasonality],
            "color": attrs.color.__dict__ if attrs.color else None,
            "pattern": attrs.pattern.__dict__ if attrs.pattern else None,
            "material": attrs.material,
            "style_tags": attrs.style_tags,
            "group_id": attrs.group_id,
            "set_role": attrs.set_role,
            "coord_set_kind": attrs.coord_set_kind,
            "set_cohesion_policy": attrs.set_cohesion_policy.value
            if attrs.set_cohesion_policy
            else None,
            "fit_profile": attrs.fit_profile.value if attrs.fit_profile else None,
            "top_length_class": attrs.top_length_class,
            "bottom_rise_class": attrs.bottom_rise_class,
            "shoulder_structure": attrs.shoulder_structure,
            "waist_emphasis": attrs.waist_emphasis,
            "skirt_silhouette": attrs.skirt_silhouette,
            "pattern_orientation": attrs.pattern_orientation,
            "leg_opening_cm": attrs.leg_opening_cm,
            "footwear_class": attrs.footwear_class,
            "bag_kind": attrs.bag_kind,
            "jewelry_kind": attrs.jewelry_kind,
            "leather_family": attrs.leather_family,
            "metal_family": attrs.metal_family,
            "metal_finish": attrs.metal_finish,
            "bag_material": attrs.bag_material,
            "updated_at": datetime.now(timezone.utc).timestamp(),
        }
