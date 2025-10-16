# TODO.md — AI Outfit Bundle Recommendation Engine (Postgres-only MVP)

This is a no-time-estimates, stepwise plan aligned to the spec and our extended AGENTS.md. No code yet.

## Phase 1: Foundation and Infrastructure

- [ ] Initialize repo with modular monolith structure reflecting bounded contexts.
- [ ] Configure pyproject.toml (pydantic, fastapi, uvicorn, alembic, psycopg, hypothesis, ruff, mypy, radon, opentelemetry optional).
- [ ] Set up pytest, coverage, ruff, mypy, radon; add pre-commit hooks.
- [ ] Create base docs: README.md, AGENTS.md (this file), CONTRIBUTING.md.
- [ ] Alembic: initialize migrations.
- [ ] Postgres schema:
  - [ ] Aggregates tables per BC using JSONB payload where appropriate.
  - [ ] Transactional outbox table (events) with indexes on status/published/occurred_at.
  - [ ] Idempotency table for request keys and cached responses.
- [ ] Background worker:
  - [ ] Outbox scanner (batch read, publish to internal handlers).
  - [ ] Dead-letter handling after retry budget.
  - [ ] Metrics for lag, success/fail counts.

## Phase 2: Core Domain — Wardrobe & Catalog

- [ ] Implement Attribute Registry (role-applicable fields, types).
- [ ] Value objects:
  - [ ] Color L*C*h° with validation and ΔE2000 operations.
  - [ ] Pattern, seasonality, formality range enums.
- [ ] Wardrobe BC:
  - [ ] Aggregates and invariants (group_id coherence, set_role if present).
  - [ ] Commands: AddItem, UpdateItem, RemoveItem (idempotent).
  - [ ] Events: ItemAdded/Updated/orRemoved.
  - [ ] Repository using JSONB and optimistic locking.
  - [ ] Tests: unit + property (role-attribute consistency; color bounds).
- [ ] Catalog BC: mirror Wardrobe BC with global scope and validations.

## Phase 3: Profile & Context

- [ ] Profile BC:
  - [ ] ProfileAggregate with baseline dressiness, default occasion, guardrails, style signature.
  - [ ] AppearanceSignature, BodySignature with optional fields.
  - [ ] Commands: SetProfile, SetAppearanceProfile, SetBodySignature, RecordFeedback.
  - [ ] Events and repositories; profile snapshot read model.
  - [ ] Tests: property-based for signature validation and guardrail coherency.
- [ ] Context BC:
  - [ ] Occasion → formality mapping; temperature band config.
  - [ ] Update commands and read models.
  - [ ] Defaulting rules for missing context.
  - [ ] Tests: inference and fallback behavior.

## Phase 4: Styling Rules

- [ ] RuleSetAggregate and schema (versioned).
- [ ] Layering graph validation (acyclic).
- [ ] Template registry (e.g., business_suit, streetwear, winter_layering, etc.).
- [ ] Coordinated set policies and accessory consistency modes.
- [ ] Weights and thresholds; config loader and validation.
- [ ] Commands: PublishRuleSet, RollbackRuleSet.
- [ ] Tests: rule validation, layering constraints, template gates.

## Phase 5: Search/Indexing (Postgres-only)

- [ ] Read models:
  - [ ] ItemSearchDoc (denormalized) stored in Postgres (table) with JSONB column for facets; include confidence fields.
- [ ] Projections:
  - [ ] Project ItemAdded/Updated/Removed and Catalog events into ItemSearchDoc.
  - [ ] Track updated_at, favorites_flag, group_id, set_role, set_cohesion_policy.
- [ ] Indexing:
  - [ ] Create GIN indexes on key JSONB paths (slot, role, formality, seasonality, style_tags).
  - [ ] Partial indexes for frequently queried subsets (e.g., by slot).
  - [ ] Optional trigram index for fuzzy style_tags/pattern searches.
- [ ] Queries:
  - [ ] Implement SearchCloset and SearchCatalog with filters per spec.
  - [ ] Cursor-based pagination (keyset where applicable).
- [ ] Tests: performance assertions on representative datasets; correctness on filters.

## Phase 6: Scoring and Constraints

- [ ] Hard constraints engine:
  - [ ] Layering order; one_piece exclusivity; strict co-ord integrity; cufflinks/belt rules; formality/event bounds; temperature safety; at-most one catalog item; coverage guardrails.
  - [ ] Early pruning hooks and violation logging.
- [ ] Soft scoring components (each pure, returns [0,1] and optional explanation):
  - [ ] PaletteHarmonyScore (ΔE and hue harmony).
  - [ ] PatternMixScore.
  - [ ] SilhouetteBalanceScore.
  - [ ] FormalityCloseness.
  - [ ] TemperatureFit.
  - [ ] StyleTagMatch.
  - [ ] Novelty/Variety.
  - [ ] AccessoryConsistencyScore (mode-dependent).
  - [ ] SkinSynergyScore (optional; near-face).
  - [ ] ProportionFitScore (optional; body heuristics).
- [ ] Tests: unit + property-based (monotonicity, bounds, confidence scaling).

## Phase 7: Candidate Retrieval and Assembly

- [ ] Candidate generation:
  - [ ] Build per-slot filter sets from context/template.
  - [ ] Limit K per slot; stable sorts where defined; explicit tie-breakers documented.
- [ ] Beam search (heuristic):
  - [ ] Configurable beam width.
  - [ ] Template selection from occasion and profile.
  - [ ] Ensemble anchor first (suits/co-ords/one-piece) then complementary slots then accessories.
  - [ ] Hard constraints enforced incrementally; prune early.
  - [ ] Soft score aggregation; explanation capture.
- [ ] Coordinated sets:
  - [ ] Strict: select full set atomically; no breaking.
  - [ ] Prefer_strict: prefer matching set; allow breaking with penalty if needed.
  - [ ] Loose: free to mix; still prefer cohesion.
- [ ] Tests: integration for multi-slot assembly; stress with co-ords and missing attributes.

Note: No determinism tests (no requirement that repeated runs produce identical outputs). Keep sanity checks for tie-breaking documentation.

## Phase 8: Replace Slot

- [ ] ReplaceSlot flow:
  - [ ] Fixed items remain; rank alternatives by unary quality + compatibility with fixed.
  - [ ] Co-ords:
    - [ ] If member of strict set → same_group only or `requires_cascade=true`.
    - [ ] Prefer_strict → try same_group first; otherwise palette/pattern cohesive with penalty.
  - [ ] Response includes alternatives with `requires_cascade` and `coherence_reason`.
- [ ] Tests: all replace scenarios including cascade plans, strict failures, and palette/pattern fallbacks.

## Phase 9: API Layer

- [ ] FastAPI app with middleware: request ID/correlation, rate limiting (Postgres-backed), error handling.
- [ ] Commands:
  - [ ] add-item, update-item, remove-item
  - [ ] set-profile, set-appearance-profile, set-body-signature
  - [ ] generate-outfit, replace-slot, record-feedback
- [ ] Queries:
  - [ ] search-closet, search-catalog
  - [ ] get-outfit-details, get-outfit-history
  - [ ] get-profile-snapshot
- [ ] Idempotency:
  - [ ] Store idempotency_key + response in Postgres; return cached response for repeats.
- [ ] Tests: contract tests for all endpoints, error model checks, pagination.

## Phase 10: Observability and Quality

- [ ] Metrics:
  - [ ] P50/P95 per endpoint; bundle_found_rate; hard_constraint_violations; acceptance_rate; swap_depth; projector lag; cache metrics (in-process LRU); OQI.
- [ ] Tracing:
  - [ ] OpenTelemetry (optional) with spans for search, scoring, beam steps, replace cascade.
- [ ] Logging:
  - [ ] Structured logs; include ruleset_version, template_id, decision points.
- [ ] Dashboards:
  - [ ] Basic dashboards for latency and error rates (adapter as available).
- [ ] Tests: verify metric emission; sample traces/log fields.

## Phase 11: Deployment and Operations (No Kubernetes)

- [ ] Alembic migrations (reversible).
- [ ] Single-process deployment or Docker Compose with Postgres.
- [ ] Health checks and readiness endpoints.
- [ ] Feature flags in config/env (percentage rollouts and cohorts).
- [ ] Backup and restore procedure for Postgres.
- [ ] Runbook for common operational issues.

## Phase 12: Quality Gates and Acceptance

- [ ] Coverage ≥95%; ruff/mypy/radon pass.
- [ ] Performance checks: P95 latency targets (generate/replace) on representative data.
- [ ] Zero hard-constraint violations across test suites.
- [ ] Bundle-found rate ≥98% on synthetic wardrobes.
- [ ] OQI computed and monitored.
- [ ] README and architecture docs updated.

## Risk Mitigation

- [ ] Retrieval hot paths: add covering/partial indexes; precompute via materialized views.
- [ ] Event lag: index outbox, tune batch size, add LISTEN/NOTIFY nudge (optional).
- [ ] Large wardrobes: tighten K, tune filters by template; paginate internal searches.
- [ ] Scoring overhead: precompute unary features in projections; micro-cache within request.
- [ ] Rate limiting without Redis: Postgres token bucket with careful upsert; monitor contention.

## Nice-to-Haves (Post-MVP Migration Paths; not in scope now)

- [ ] Optional external search engine with hybrid retrieval and semantic rerank.
- [ ] Separate services for Search/Indexing and Recommendation if SLOs demand.
- [ ] Advanced feature flags service; cohort experimentation framework.
- [ ] Learned scoring models with online monitoring and fallback to heuristic beam search.