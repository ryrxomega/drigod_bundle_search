import math
from typing import Optional

from outfit_engine.domain import AppearanceSignature, BodySignature, ColorLCh, TorsoLegRatio
from outfit_engine.domain.models import ItemAttributes


class ScoringEngine:
    def __init__(self, weights: dict[str, float]):
        self.weights = weights

    def compute_palette_harmony(self, items: list[ItemAttributes]) -> float:
        colors = [item.color for item in items if item.color]
        if len(colors) < 2:
            return 1.0

        harmony_score = 0.0
        count = 0
        for i, c1 in enumerate(colors):
            for c2 in colors[i + 1 :]:
                hue_diff = abs(c1.h - c2.h)
                hue_diff = min(hue_diff, 360 - hue_diff)

                if hue_diff <= 30:
                    harmony_score += 1.0
                elif 150 <= hue_diff <= 210:
                    harmony_score += 0.9
                elif 110 <= hue_diff <= 130:
                    harmony_score += 0.85
                else:
                    harmony_score += 0.6

                count += 1

        return harmony_score / count if count > 0 else 1.0

    def compute_pattern_mix(self, items: list[ItemAttributes]) -> float:
        patterns = [item.pattern for item in items if item.pattern and item.pattern.type]
        if len(patterns) <= 1:
            return 1.0

        pattern_count = len(patterns)
        if pattern_count == 2:
            return 0.9
        elif pattern_count == 3:
            return 0.7
        else:
            return 0.5

    def compute_silhouette_balance(self, items: list[ItemAttributes]) -> float:
        top_items = [item for item in items if item.slot in ["top", "one_piece"]]
        bottom_items = [item for item in items if item.slot == "bottom"]

        if not top_items or not bottom_items:
            return 1.0

        fit_balance = 0.0
        count = 0
        for top in top_items:
            for bottom in bottom_items:
                if top.fit_profile and bottom.fit_profile:
                    if (
                        top.fit_profile.value == "oversized"
                        and bottom.fit_profile.value in ["slim", "regular"]
                    ):
                        fit_balance += 1.0
                    elif (
                        top.fit_profile.value in ["slim", "regular"]
                        and bottom.fit_profile.value == "relaxed"
                    ):
                        fit_balance += 0.9
                    else:
                        fit_balance += 0.8
                    count += 1

        return fit_balance / count if count > 0 else 1.0

    def compute_formality_closeness(
        self, items: list[ItemAttributes], target_formality: int
    ) -> float:
        if not items:
            return 0.0

        total_deviation = sum(abs(item.formality - target_formality) for item in items)
        avg_deviation = total_deviation / len(items)

        if avg_deviation <= 0.5:
            return 1.0
        elif avg_deviation <= 1.0:
            return 0.9
        elif avg_deviation <= 1.5:
            return 0.7
        else:
            return 0.5

    def compute_temperature_fit(
        self, items: list[ItemAttributes], temperature_band: str
    ) -> float:
        seasonality_match_score = 0.0
        count = 0

        for item in items:
            if item.seasonality:
                if temperature_band in [s.value for s in item.seasonality]:
                    seasonality_match_score += 1.0
                else:
                    seasonality_match_score += 0.5
                count += 1

        return seasonality_match_score / count if count > 0 else 0.8

    def compute_style_tag_match(
        self, items: list[ItemAttributes], profile_style_tags: list[str]
    ) -> float:
        if not profile_style_tags:
            return 1.0

        matches = 0
        total_tags = 0

        for item in items:
            for tag in item.style_tags:
                total_tags += 1
                if tag in profile_style_tags:
                    matches += 1

        return matches / total_tags if total_tags > 0 else 0.8

    def compute_novelty(self, items: list[ItemAttributes], recently_worn: list[str]) -> float:
        if not recently_worn:
            return 1.0

        item_ids = {item.role for item in items}
        overlap = len([r for r in recently_worn if r in item_ids])

        return max(0.5, 1.0 - (overlap * 0.15))

    def compute_accessory_consistency(self, items: list[ItemAttributes], mode: str) -> float:
        if mode == "OFF":
            return 1.0

        leather_items = [item for item in items if item.leather_family]
        metal_items = [item for item in items if item.metal_family]

        consistency_score = 1.0

        if leather_items:
            families = {item.leather_family for item in leather_items}
            if len(families) > 2:
                consistency_score *= 0.8 if mode == "SOFT" else 0.5

        if metal_items:
            families = {item.metal_family for item in metal_items}
            if len(families) > 2:
                consistency_score *= 0.8 if mode == "SOFT" else 0.5

        return consistency_score

    def compute_skin_synergy(
        self,
        items: list[ItemAttributes],
        appearance: Optional[AppearanceSignature],
        near_face_slots: list[str],
    ) -> tuple[float, list[str]]:
        if not appearance or not appearance.skin_lch:
            return 1.0, []

        explanations = []
        synergy_score = 1.0
        count = 0

        for item in items:
            if item.slot not in near_face_slots or not item.color:
                continue

            count += 1
            skin_color = appearance.skin_lch
            item_color = item.color

            hue_diff = abs(skin_color.h - item_color.h)
            hue_diff = min(hue_diff, 360 - hue_diff)

            if hue_diff <= 20:
                synergy_score *= 0.95
                explanations.append(f"Near-face color harmonious (Δh {hue_diff:.0f}°)")
            elif 160 <= hue_diff <= 200:
                synergy_score *= 1.05
                explanations.append(f"Near-face color complementary (Δh {hue_diff:.0f}°)")

            l_diff = abs(skin_color.L - item_color.L)
            if l_diff >= 18:
                synergy_score *= 1.02
            elif l_diff < 10:
                synergy_score *= 0.93

        return min(synergy_score, 1.0), explanations

    def compute_proportion_fit(
        self, items: list[ItemAttributes], body: Optional[BodySignature]
    ) -> tuple[float, list[str]]:
        if not body:
            return 1.0, []

        explanations = []
        proportion_score = 1.0

        for item in items:
            if body.torso_leg_ratio == TorsoLegRatio.LONG_TORSO:
                if item.bottom_rise_class == "high":
                    proportion_score *= 1.05
                    explanations.append("High-rise bottoms balance long torso")
                if item.top_length_class == "longline":
                    proportion_score *= 0.95

            elif body.torso_leg_ratio == TorsoLegRatio.LONG_LEGS:
                if item.bottom_rise_class in ["mid", "low"]:
                    proportion_score *= 1.03
                if item.top_length_class == "longline":
                    proportion_score *= 1.02

            if body.waist_definition and item.waist_emphasis:
                if (
                    body.waist_definition.value == "defined"
                    and item.waist_emphasis in ["belted", "darted", "wrap", "empire"]
                ):
                    proportion_score *= 1.03
                    explanations.append("Waist emphasis complements defined waist")

        return min(proportion_score, 1.0), explanations

    def compute_total_score(
        self,
        items: list[ItemAttributes],
        target_formality: int,
        temperature_band: str,
        profile_style_tags: list[str],
        recently_worn: list[str],
        accessory_mode: str,
        appearance: Optional[AppearanceSignature],
        body: Optional[BodySignature],
        near_face_slots: list[str],
    ) -> tuple[float, dict[str, float], list[str]]:
        palette = self.compute_palette_harmony(items)
        pattern = self.compute_pattern_mix(items)
        silhouette = self.compute_silhouette_balance(items)
        formality = self.compute_formality_closeness(items, target_formality)
        temperature = self.compute_temperature_fit(items, temperature_band)
        style = self.compute_style_tag_match(items, profile_style_tags)
        variety = self.compute_novelty(items, recently_worn)
        consistency = self.compute_accessory_consistency(items, accessory_mode)
        skin_synergy, skin_explanations = self.compute_skin_synergy(
            items, appearance, near_face_slots
        )
        proportion, proportion_explanations = self.compute_proportion_fit(items, body)

        scores = {
            "palette": palette,
            "pattern": pattern,
            "silhouette": silhouette,
            "formality": formality,
            "temperature": temperature,
            "style": style,
            "variety": variety,
            "consistency": consistency,
            "skin_synergy": skin_synergy,
            "proportion": proportion,
        }

        total = sum(scores[key] * self.weights.get(key, 0.0) for key in scores)

        explanations = skin_explanations + proportion_explanations

        return total, scores, explanations
