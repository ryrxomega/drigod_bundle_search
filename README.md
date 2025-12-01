# AI Outfit Bundle Recommendation Engine

A comprehensive, category- and gender-agnostic outfit recommendation system implementing Domain-Driven Design (DDD) and CQRS architecture.

## Overview

This engine generates coherent outfit bundles from a user's wardrobe and optional catalog, with deterministic behavior for the same inputs. It enforces hard constraints, optimizes soft preferences, and supports:

- **Skin-tone color synergy** (optional, soft scoring)
- **Body proportion/shape preferences** (optional, soft scoring)
- **Coordinated sets (co-ords)** with configurable cohesion policies
- **Multiple occasion templates** (business, casual, formal, streetwear, etc.)
- **Beam search algorithm** for optimal outfit assembly

## Key Features

- **Category-agnostic**: Works with any garment categories, not hardcoded to specific types
- **Gender-neutral**: Mens/womens/unisex are attributes, not assumptions
- **Deterministic**: Same inputs + configuration = same output
- **Flexible constraints**: Hard constraints (must pass) and soft preferences (scored)
- **Coordinated sets**: Supports suits, tracksuits, knit sets, co-ord separates, etc.
- **Replace flow**: Swap individual slots with cascade planning for co-ords
- **Event-driven**: CQRS architecture with domain events
- **Sparse data model**: Items only store applicable attributes

## Architecture

### Bounded Contexts

- **Wardrobe BC**: User wardrobe items
- **Catalog BC**: Global catalog items
- **Profile BC**: User profiles, appearance, body signatures
- **Context BC**: Occasion mappings, temperature bands
- **Styling Rules BC**: Versioned rule sets
- **Search/Indexing BC**: Fast candidate retrieval
- **Recommendation BC**: Outfit generation orchestration
- **Quality/Evaluation BC**: Metrics and experiments

### Technology Stack

- **Python 3.11+**
- **FastAPI**: REST API framework
- **Pydantic**: Data validation
- **In-memory storage**: For development (production would use PostgreSQL + search index)

## Installation

```bash
# Install dependencies
pip install poetry
poetry install

# Or with pip
pip install -e .
```

## Running the Service

```bash
# Development server
uvicorn outfit_engine.api.app:app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn outfit_engine.api.app:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Endpoints

### Commands (v1)

- `POST /api/v1/commands/add-item` - Add item to wardrobe
- `POST /api/v1/commands/update-item` - Update wardrobe item
- `POST /api/v1/commands/remove-item` - Remove wardrobe item
- `POST /api/v1/commands/set-profile` - Set user profile
- `POST /api/v1/commands/set-appearance-profile` - Set appearance signature
- `POST /api/v1/commands/set-body-signature` - Set body signature
- `POST /api/v1/commands/generate-outfit` - Generate outfit bundle
- `POST /api/v1/commands/replace-slot` - Replace slot in outfit
- `POST /api/v1/commands/record-feedback` - Record user feedback

### Example: Generate Outfit

```bash
curl -X POST http://localhost:8000/api/v1/commands/generate-outfit \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-123",
    "mode": "ad_hoc",
    "context": {
      "occasion": "work_office",
      "target_dressiness": 4,
      "temperature_band": "warm"
    },
    "allow_catalog": false
  }'
```

### Example: Add Item with Appearance and Body Context

```bash
# Set appearance profile
curl -X POST http://localhost:8000/api/v1/commands/set-appearance-profile \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-123",
    "appearance_signature": {
      "skin_lch": {"L": 72.5, "C": 18.0, "h": 55.0},
      "undertone": "warm",
      "synergy_style": "contrast"
    }
  }'

# Set body signature
curl -X POST http://localhost:8000/api/v1/commands/set-body-signature \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-123",
    "body_signature": {
      "height_class": "petite",
      "torso_leg_ratio": "long_torso",
      "waist_definition": "defined",
      "fit_pref": "regular"
    }
  }'

# Add item
curl -X POST http://localhost:8000/api/v1/commands/add-item \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-123",
    "item": {
      "role": "shirt",
      "slot": "top",
      "formality": 4,
      "seasonality": ["warm", "cool"],
      "color": {"L": 95, "C": 2, "h": 180},
      "style_tags": ["smart", "minimal"],
      "fit_profile": "slim",
      "top_length_class": "regular"
    }
  }'
```

## Testing

```bash
# Run tests
poetry run pytest

# With coverage
poetry run pytest --cov=outfit_engine --cov-report=html
```

## Configuration

The rule set, weights, and templates are configured in `src/outfit_engine/config/bootstrap.py`.

### Scoring Weights (default)

- Palette harmony: 0.22
- Pattern mixing: 0.12
- Silhouette balance: 0.12
- Formality closeness: 0.14
- Temperature fit: 0.10
- Style tag match: 0.08
- Novelty/variety: 0.05
- Accessory consistency: 0.07
- Skin synergy: 0.08
- Body proportion: 0.10

## Domain Model

### Item Attributes

Items have sparse, role-applicable attributes:

- **Core**: role, slot, category, formality, seasonality, color (L*C*h°), pattern, material, style_tags
- **Fit**: fit_profile, top_length_class, bottom_rise_class, shoulder_structure
- **Coordinated sets**: group_id, set_role, coord_set_kind, set_cohesion_policy
- **Accessories**: leather_family, metal_family, metal_finish, bag_kind, jewelry_kind, footwear_class

### Coordinated Sets

Items can form coordinated sets (suits, tracksuits, co-ord separates):

- **strict**: Must be worn together
- **prefer_strict**: Prefer same group; breaking allowed with penalty
- **loose**: Suggestion only

### Appearance Signature

Optional user appearance data for skin-tone synergy scoring:

- skin_lch (L*C*h° color)
- undertone (warm/cool/neutral)
- hair_lch, eye_lch (optional)
- synergy_style (contrast/harmonize/auto)

### Body Signature

Optional body proportion preferences:

- height_class (petite/average/tall)
- torso_leg_ratio (long_torso/balanced/long_legs)
- shoulder_to_hip_ratio
- waist_definition (defined/straight)
- fit_pref (slim/regular/relaxed)

## Algorithms

### Beam Search

The core assembly algorithm:

1. Start with empty outfit
2. For each slot in template order:
   - Retrieve top K candidates
   - Extend beam paths with valid items
   - Score each path
   - Keep top N paths (beam width)
3. Return highest scoring complete outfit

### Scoring Components

- **Palette Harmony**: Color relationships (analogous, complementary, triadic)
- **Pattern Mixing**: Limit patterns, prefer scale diversity
- **Silhouette Balance**: Volume distribution (oversized top + fitted bottom)
- **Formality Closeness**: Match target formality level
- **Temperature Fit**: Seasonality alignment
- **Style Tag Match**: Match user style preferences
- **Novelty**: Avoid recently worn items
- **Accessory Consistency**: Leather/metal family matching
- **Skin Synergy**: Near-face color relationships with skin tone
- **Proportion Fit**: Rise, length, structure match body proportions

## Performance Targets

- **Generate Outfit P95**: ≤ 400 ms
- **Replace Slot P95**: ≤ 600 ms
- **Bundle Found Rate**: ≥ 98%
- **Hard Constraint Violations**: 0

## License

Proprietary
