from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class Template:
    template_id: str
    slots: List[str]
    optional_slots: List[str]
    target_formality_range: tuple[int, int]
    accessory_mode: str


TEMPLATES: Dict[str, Template] = {
    "business_suit": Template(
        template_id="business_suit",
        slots=["top", "bottom", "footwear"],
        optional_slots=["outerwear", "accessory"],
        target_formality_range=(4, 5),
        accessory_mode="HARD",
    ),
    "business_smart_separates": Template(
        template_id="business_smart_separates",
        slots=["top", "bottom", "footwear"],
        optional_slots=["outerwear", "accessory"],
        target_formality_range=(3, 4),
        accessory_mode="SOFT",
    ),
    "casual_day": Template(
        template_id="casual_day",
        slots=["top", "bottom", "footwear"],
        optional_slots=["outerwear", "accessory"],
        target_formality_range=(1, 3),
        accessory_mode="OFF",
    ),
    "streetwear": Template(
        template_id="streetwear",
        slots=["top", "bottom", "footwear"],
        optional_slots=["outerwear", "accessory"],
        target_formality_range=(1, 2),
        accessory_mode="OFF",
    ),
    "winter_layering": Template(
        template_id="winter_layering",
        slots=["top", "bottom", "footwear", "outerwear"],
        optional_slots=["accessory", "legwear"],
        target_formality_range=(2, 4),
        accessory_mode="SOFT",
    ),
    "black_tie_dress": Template(
        template_id="black_tie_dress",
        slots=["one_piece", "footwear"],
        optional_slots=["accessory", "outerwear"],
        target_formality_range=(5, 5),
        accessory_mode="HARD",
    ),
}
