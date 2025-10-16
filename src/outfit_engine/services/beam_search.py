import hashlib
import random
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from outfit_engine.domain import AppearanceSignature, BodySignature
from outfit_engine.domain.models import ItemAttributes, OutfitSlot
from outfit_engine.services.scoring import ScoringEngine
from outfit_engine.services.templates import Template


@dataclass(slots=True)
class BeamPath:
    items: List[ItemAttributes]
    slots_assigned: Dict[str, ItemAttributes]
    score: float


class BeamSearchEngine:
    def __init__(self, beam_width: int = 20):
        self.beam_width = beam_width

    def generate_outfit(
        self,
        template: Template,
        candidates_by_slot: Dict[str, List[ItemAttributes]],
        scorer: ScoringEngine,
        target_formality: int,
        temperature_band: str,
        profile_style_tags: List[str],
        recently_worn: List[str],
        appearance: Optional[AppearanceSignature],
        body: Optional[BodySignature],
        near_face_slots: List[str],
        determinism_seed: Optional[str] = None,
    ) -> Optional[Tuple[List[OutfitSlot], dict, List[str]]]:
        if determinism_seed:
            seed_val = int(hashlib.sha256(determinism_seed.encode()).hexdigest(), 16) % (
                2**32
            )
            random.seed(seed_val)

        beams = [BeamPath(items=[], slots_assigned={}, score=0.0)]

        all_slots = template.slots + template.optional_slots

        for slot in all_slots:
            if slot not in candidates_by_slot or not candidates_by_slot[slot]:
                continue

            new_beams: List[BeamPath] = []

            for beam in beams:
                for candidate in candidates_by_slot[slot][: min(10, len(candidates_by_slot[slot]))]:
                    if not self._check_hard_constraints(
                        beam.items + [candidate], slot, candidate
                    ):
                        continue

                    new_items = beam.items + [candidate]
                    total_score, scores, explanations = scorer.compute_total_score(
                        new_items,
                        target_formality,
                        temperature_band,
                        profile_style_tags,
                        recently_worn,
                        template.accessory_mode,
                        appearance,
                        body,
                        near_face_slots,
                    )

                    new_slots = beam.slots_assigned.copy()
                    new_slots[slot] = candidate

                    new_beams.append(
                        BeamPath(
                            items=new_items, slots_assigned=new_slots, score=total_score
                        )
                    )

            new_beams.sort(key=lambda x: x.score, reverse=True)
            beams = new_beams[: self.beam_width]

            if not beams:
                break

        if not beams:
            return None

        best_beam = beams[0]

        outfit_slots: List[OutfitSlot] = []

        for slot, item in best_beam.slots_assigned.items():
            outfit_slots.append(OutfitSlot(slot=slot, item_id=item.item_id, source=item.source))

        final_score, final_scores, final_explanations = scorer.compute_total_score(
            best_beam.items,
            target_formality,
            temperature_band,
            profile_style_tags,
            recently_worn,
            template.accessory_mode,
            appearance,
            body,
            near_face_slots,
        )

        return outfit_slots, final_scores, final_explanations

    def _check_hard_constraints(
        self, items: List[ItemAttributes], slot: str, new_item: ItemAttributes
    ) -> bool:
        top_count = sum(1 for item in items if item.slot == "top")
        one_piece_count = sum(1 for item in items if item.slot == "one_piece")

        if one_piece_count > 0 and (top_count > 0 or slot == "top"):
            return False

        if slot == "one_piece" and top_count > 0:
            return False

        for item in items:
            if item.group_id and new_item.group_id and item.group_id == new_item.group_id:
                if item.set_cohesion_policy and item.set_cohesion_policy.value == "strict":
                    if item.set_role != new_item.set_role:
                        return False

        return True
