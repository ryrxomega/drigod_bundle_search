from functools import lru_cache

from outfit_engine.domain.models import ContextPolicy, RuleSet
from outfit_engine.infrastructure.repositories import (
    CatalogRepository,
    FeedbackRepository,
    OutfitRepository,
    ProfileRepository,
    SearchIndex,
    WardrobeRepository,
)
from outfit_engine.services.beam_search import BeamSearchEngine
from outfit_engine.services.command_handlers import CommandHandler
from outfit_engine.services.recommendation_service import RecommendationService
from outfit_engine.services.scoring import ScoringEngine


@lru_cache
def get_repositories():
    wardrobe_repo = WardrobeRepository()
    catalog_repo = CatalogRepository()
    profile_repo = ProfileRepository()
    outfit_repo = OutfitRepository()
    feedback_repo = FeedbackRepository()
    search_index = SearchIndex()

    return (
        wardrobe_repo,
        catalog_repo,
        profile_repo,
        outfit_repo,
        feedback_repo,
        search_index,
    )


@lru_cache
def get_ruleset() -> RuleSet:
    return RuleSet(
        ruleset_version="ruleset-2025-06",
        layering_graph={"base": ["mid"], "mid": ["outer"], "outer": []},
        coordinated_sets={
            "default_cohesion": "prefer_strict",
            "palette_threshold_deltaE00": 12.0,
        },
        accessory_consistency={
            "leather": {
                "business_suit": {"shoes_belt": "HARD"},
            },
            "metal": {
                "business_suit": {"cufflinks_watch": "HARD"},
            },
        },
        weights={
            "palette": 0.22,
            "pattern": 0.12,
            "silhouette": 0.12,
            "formality": 0.14,
            "temperature": 0.10,
            "style": 0.08,
            "variety": 0.05,
            "consistency": 0.07,
            "skin_synergy": 0.08,
            "proportion": 0.10,
        },
        skin_synergy={
            "near_face_slots": ["top", "one_piece", "neckwear", "scarf", "hat"],
        },
        body_proportion={},
        template_ranking={},
    )


@lru_cache
def get_context_policy() -> ContextPolicy:
    return ContextPolicy(
        target_formality_by_occasion={
            "work_office": (3, 4),
            "formal_event": (4, 5),
            "casual_day": (1, 3),
        },
        accessory_defaults_by_occasion={
            "formal_event": ["watch", "pocket_square"],
        },
        temperature_bands={
            "hot": (28, 50),
            "warm": (18, 27),
            "cool": (10, 17),
            "cold": (-20, 9),
        },
    )


@lru_cache
def get_scorer() -> ScoringEngine:
    ruleset = get_ruleset()
    return ScoringEngine(weights=ruleset.weights)


@lru_cache
def get_beam_search() -> BeamSearchEngine:
    return BeamSearchEngine(beam_width=20)


@lru_cache
def get_recommendation_service() -> RecommendationService:
    (
        wardrobe_repo,
        catalog_repo,
        profile_repo,
        outfit_repo,
        feedback_repo,
        search_index,
    ) = get_repositories()

    scorer = get_scorer()
    beam_search = get_beam_search()

    return RecommendationService(
        search_index=search_index,
        profile_repo=profile_repo,
        outfit_repo=outfit_repo,
        scorer=scorer,
        beam_search=beam_search,
    )


@lru_cache
def get_command_handler() -> CommandHandler:
    (
        wardrobe_repo,
        catalog_repo,
        profile_repo,
        outfit_repo,
        feedback_repo,
        search_index,
    ) = get_repositories()

    recommendation_service = get_recommendation_service()
    ruleset = get_ruleset()
    context_policy = get_context_policy()

    return CommandHandler(
        wardrobe_repo=wardrobe_repo,
        catalog_repo=catalog_repo,
        profile_repo=profile_repo,
        outfit_repo=outfit_repo,
        feedback_repo=feedback_repo,
        search_index=search_index,
        recommendation_service=recommendation_service,
        ruleset=ruleset,
        context_policy=context_policy,
    )
