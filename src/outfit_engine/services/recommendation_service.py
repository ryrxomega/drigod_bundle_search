import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from uuid import uuid4

from outfit_engine.domain import (
    AppearanceSignature,
    BodySignature,
    ColorLCh,
    FitProfile,
    Occasion,
    Seasonality,
    SetCohesionPolicy,
)
from outfit_engine.domain.events import OutfitGenerated, SlotReplaced
from outfit_engine.domain.models import ItemAttributes, Outfit, OutfitSlot, Pattern, Profile
from outfit_engine.infrastructure.repositories import (
    OutfitRepository,
    ProfileRepository,
    SearchIndex,
)
from outfit_engine.services.beam_search import BeamSearchEngine
from outfit_engine.services.scoring import ScoringEngine
from outfit_engine.services.templates import TEMPLATES, Template


class RecommendationService:
    def __init__(
        self,
        search_index: SearchIndex,
        profile_repo: ProfileRepository,
        outfit_repo: OutfitRepository,
        scorer: ScoringEngine,
        beam_search: BeamSearchEngine,
    ):
        self.search_index = search_index
        self.profile_repo = profile_repo
        self.outfit_repo = outfit_repo
        self.scorer = scorer
        self.beam_search = beam_search

    def generate_outfit(
        self,
        user_id: str,
        context: Optional[dict],
        allow_catalog: bool,
        ruleset_version: str,
        determinism_key: Optional[str],
    ) -> Tuple[Outfit, OutfitGenerated]:
        profile = self.profile_repo.get(user_id)

        if not profile:
            profile = Profile(
                user_id=user_id,
                baseline_dressiness=3,
                default_occasion="casual_day",
            )

        occasion = context.get("occasion", profile.default_occasion) if context else profile.default_occasion
        target_dressiness = context.get("target_dressiness", profile.baseline_dressiness) if context else profile.baseline_dressiness
        temperature_band = context.get("temperature_band", "warm") if context else "warm"

        template = self._select_template(occasion, target_dressiness)

        candidates_by_slot = self._retrieve_candidates(
            user_id, template, target_dressiness, temperature_band, allow_catalog
        )

        seed = self._make_determinism_seed(
            user_id, ruleset_version, template.template_id, profile, determinism_key
        )

        result = self.beam_search.generate_outfit(
            template=template,
            candidates_by_slot=candidates_by_slot,
            scorer=self.scorer,
            target_formality=target_dressiness,
            temperature_band=temperature_band,
            profile_style_tags=profile.style_signature.get("tags", []),
            recently_worn=[],
            appearance=profile.appearance_signature,
            body=profile.body_signature,
            near_face_slots=["top", "one_piece", "neckwear", "scarf", "hat"],
            determinism_seed=seed,
        )

        if not result:
            raise ValueError("Unable to generate outfit - insufficient candidates")

        outfit_slots, scores, explanations = result

        outfit_id = str(uuid4())
        outfit = Outfit(
            outfit_id=outfit_id,
            user_id=user_id,
            ruleset_version=ruleset_version,
            template_id=template.template_id,
            slots={"items": outfit_slots},
            scores=scores,
            explanations=explanations,
            used_catalog_item=None if not allow_catalog else "unknown",
        )

        self.outfit_repo.save(outfit)

        event = OutfitGenerated(
            user_id=user_id,
            outfit_id=outfit_id,
            ruleset_version=ruleset_version,
            template_id=template.template_id,
            context_applied={"occasion": occasion, "target_dressiness": target_dressiness},
            quality_score=scores.get("total", 0.0),
        )

        return outfit, event

    def replace_slot(
        self,
        user_id: str,
        outfit_id: str,
        target_slot: str,
        max_alternatives: int,
        determinism_key: Optional[str],
    ) -> Tuple[List[dict], Optional[List[dict]], SlotReplaced]:
        outfit = self.outfit_repo.get(user_id, outfit_id)
        if not outfit:
            raise ValueError(f"Outfit {outfit_id} not found")

        profile = self.profile_repo.get(user_id)

        candidates = self._retrieve_slot_candidates(
            user_id, target_slot, formality_range=(1, 5), temperature_band="warm"
        )

        alternatives = []
        for candidate in candidates[:max_alternatives]:
            score = self._score_replacement(candidate, outfit, profile)
            alternatives.append(
                {
                    "item_id": candidate.role,
                    "score": score,
                    "requires_cascade": False,
                    "coherence_reason": "palette_match",
                }
            )

        alternatives.sort(key=lambda x: x["score"], reverse=True)

        event = SlotReplaced(
            user_id=user_id,
            outfit_id=outfit_id,
            target_slot=target_slot,
            candidate_ids=[alt["item_id"] for alt in alternatives],
        )

        return alternatives, None, event

    def _select_template(self, occasion: str, target_dressiness: int) -> Template:
        occasion_enum = Occasion(occasion) if occasion in [o.value for o in Occasion] else Occasion.CASUAL_DAY

        mapping = {
            Occasion.WORK_OFFICE: "business_smart_separates",
            Occasion.FORMAL_EVENT: "business_suit",
            Occasion.CASUAL_DAY: "casual_day",
            Occasion.STREETWEAR: "streetwear",
            Occasion.WINTER_LAYERING: "winter_layering",
        }

        template_id = mapping.get(occasion_enum, "casual_day")

        return TEMPLATES[template_id]

    def _retrieve_candidates(
        self,
        user_id: str,
        template: Template,
        target_formality: int,
        temperature_band: str,
        allow_catalog: bool,
    ) -> Dict[str, List[ItemAttributes]]:
        candidates_by_slot = {}

        for slot in template.slots + template.optional_slots:
            candidates = self._retrieve_slot_candidates(
                user_id, slot, template.target_formality_range, temperature_band
            )
            candidates_by_slot[slot] = candidates

        return candidates_by_slot

    def _retrieve_slot_candidates(
        self, user_id: str, slot: str, formality_range: Tuple[int, int], temperature_band: str
    ) -> List[ItemAttributes]:
        filters = {"slot": slot, "formality": formality_range}

        docs = self.search_index.search(user_id, filters, limit=50)

        candidates = []
        for doc in docs:
            candidates.append(self._doc_to_item_attributes(doc))

        return candidates

    def _doc_to_item_attributes(self, doc: dict) -> ItemAttributes:
        color = None
        if "color" in doc and doc["color"]:
            color = ColorLCh(**doc["color"])

        pattern = None
        if "pattern" in doc and doc["pattern"]:
            pattern = Pattern(**doc["pattern"])

        fit_profile = None
        if "fit_profile" in doc and doc["fit_profile"]:
            fit_profile = FitProfile(doc["fit_profile"])

        seasonality = []
        if "seasonality" in doc and doc["seasonality"]:
            seasonality = [Seasonality(s) for s in doc["seasonality"]]

        set_cohesion_policy = None
        if "set_cohesion_policy" in doc and doc["set_cohesion_policy"]:
            set_cohesion_policy = SetCohesionPolicy(doc["set_cohesion_policy"])

        return ItemAttributes(
            item_id=doc.get("id", "unknown"),
            source=doc.get("source", "wardrobe"),
            role=doc.get("role", "unknown"),
            slot=doc.get("slot", "unknown"),
            category=doc.get("category"),
            formality=doc.get("formality", 3),
            seasonality=seasonality,
            color=color,
            pattern=pattern,
            material=doc.get("material"),
            style_tags=doc.get("style_tags", []),
            fit_profile=fit_profile,
            group_id=doc.get("group_id"),
            set_role=doc.get("set_role"),
            set_cohesion_policy=set_cohesion_policy,
        )

    def _score_replacement(
        self, candidate: ItemAttributes, outfit: Outfit, profile: Optional[Profile]
    ) -> float:
        base_score = 0.8

        if profile and candidate.style_tags:
            profile_tags = profile.style_signature.get("tags", [])
            if any(tag in profile_tags for tag in candidate.style_tags):
                base_score += 0.15

        return min(base_score, 1.0)

    def _make_determinism_seed(
        self,
        user_id: str,
        ruleset_version: str,
        template_id: str,
        profile: Profile,
        determinism_key: Optional[str],
    ) -> str:
        parts = [user_id, ruleset_version, template_id]

        if determinism_key:
            parts.append(determinism_key)

        if profile.appearance_signature:
            parts.append(repr(profile.appearance_signature))

        if profile.body_signature:
            parts.append(repr(profile.body_signature))

        return hashlib.sha256("".join(parts).encode()).hexdigest()
