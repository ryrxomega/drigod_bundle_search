from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Seasonality(Enum):
    HOT = "hot"
    WARM = "warm"
    COOL = "cool"
    COLD = "cold"


class FitProfile(Enum):
    SLIM = "slim"
    REGULAR = "regular"
    RELAXED = "relaxed"
    OVERSIZED = "oversized"
    CROPPED = "cropped"


class GenderMarket(Enum):
    MENS = "mens"
    WOMENS = "womens"
    UNISEX = "unisex"


class SetCohesionPolicy(Enum):
    STRICT = "strict"
    PREFER_STRICT = "prefer_strict"
    LOOSE = "loose"


class Undertone(Enum):
    WARM = "warm"
    COOL = "cool"
    NEUTRAL = "neutral"


class SynergyStyle(Enum):
    CONTRAST = "contrast"
    HARMONIZE = "harmonize"
    AUTO = "auto"


class HeightClass(Enum):
    PETITE = "petite"
    AVERAGE = "average"
    TALL = "tall"


class TorsoLegRatio(Enum):
    LONG_TORSO = "long_torso"
    BALANCED = "balanced"
    LONG_LEGS = "long_legs"


class ShoulderToHipRatio(Enum):
    BROAD_SHOULDERS = "broad_shoulders"
    BALANCED = "balanced"
    BROAD_HIPS = "broad_hips"


class WaistDefinition(Enum):
    DEFINED = "defined"
    STRAIGHT = "straight"


class FitPreference(Enum):
    SLIM = "slim"
    REGULAR = "regular"
    RELAXED = "relaxed"


class TemperatureBand(Enum):
    HOT = "hot"
    WARM = "warm"
    COOL = "cool"
    COLD = "cold"


class Occasion(Enum):
    WORK_OFFICE = "work_office"
    WORK_CASUAL = "work_casual"
    CASUAL_DAY = "casual_day"
    DATE_NIGHT = "date_night"
    FORMAL_EVENT = "formal_event"
    COCKTAIL_EVENING = "cocktail_evening"
    WEDDING_GUEST = "wedding_guest"
    STREETWEAR = "streetwear"
    ATHLEISURE = "athleisure"
    ACTIVE_GYM = "active_gym"
    BEACH_RESORT = "beach_resort"
    FESTIVAL_CONCERT = "festival_concert"
    TRAVEL_AIRPORT = "travel_airport"
    WINTER_LAYERING = "winter_layering"
    RAINWEAR_TECHNICAL = "rainwear_technical"
    CREATIVE_PROFESSIONAL = "creative_professional"


@dataclass(frozen=True)
class ColorLCh:
    L: float
    C: float
    h: float

    def delta_e(self, other: "ColorLCh") -> float:
        # simplified approximation using Euclidean distance in LCh space
        return ((self.L - other.L) ** 2 + (self.C - other.C) ** 2 + (self.h - other.h) ** 2) ** 0.5


@dataclass(slots=True)
class Pattern:
    type: Optional[str] = None
    scale: Optional[str] = None


@dataclass(slots=True)
class AppearanceSignature:
    skin_lch: Optional[ColorLCh] = None
    undertone: Optional[Undertone] = None
    hair_lch: Optional[ColorLCh] = None
    eye_lch: Optional[ColorLCh] = None
    synergy_style: Optional[SynergyStyle] = None


@dataclass(slots=True)
class BodySignature:
    height_class: Optional[HeightClass] = None
    torso_leg_ratio: Optional[TorsoLegRatio] = None
    shoulder_to_hip_ratio: Optional[ShoulderToHipRatio] = None
    waist_definition: Optional[WaistDefinition] = None
    fit_pref: Optional[FitPreference] = None
    notes: list[str] = field(default_factory=list)
