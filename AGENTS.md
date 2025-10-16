# AGENTS.md: AI Outfit Recommendation Engine Development Constitution

This document outlines the principles, processes, and quality standards for the AI Outfit Bundle Recommendation Engine project. All agents must adhere to these guidelines to ensure we build a high-quality, maintainable, and understandable system.

## 1. Core Philosophy

1.  **Domain == Documentation == Code:** The domain model, documentation, and source code are different representations of the same reality and must always be synchronized.
2.  **Quality is a Trajectory:** Every commit must demonstrably improve the overall quality of the product.
3.  **Performance as a Feature:** Every component must be designed with the P95 latency targets in mind (400ms for generation, 600ms for replacement). Performance testing is not optional.
4.  **Determinism is Sacred:** The same inputs with the same configuration must always produce the same outfit. This is critical for debugging and user trust.
5.  **Graceful Degradation:** When optional features (skin-tone synergy, body proportions) lack data, the system must continue to function with neutral scoring.

## 2. General Development Methodology

We adhere to a strict methodology that combines Domain-Driven Design, Literate Programming, and Test-Driven Development.

### 2.1. Domain-Driven Design (DDD)
The code's structure must mirror the domain model. Use the Ubiquitous Language consistently.

### 2.2. Literate Programming
Code MUST be written as a narrative, optimized for human understanding.
-   **Docstrings:** Every module, class, and function must have a comprehensive Google-style docstring.
-   **Comments:** Use inline comments to explain the "why" behind complex logic.

### 2.3. Test-Driven Development (TDD)
All development MUST follow the strict "Red-Green-Refactor" cycle.

### 2.4. AICODE- Comment Prefixes
Use these prefixes to structure your thought process and tasks within the code:
-   `AICODE-NOTE`: Notes for other agents or your future self.
-   `AICODE-TODO`: A task to be addressed later.
-   `AICODE-PSEUDO`: Pseudocode before implementation.
-   `AICODE-MATH`: In-depth mathematical reasoning.

## 3. Domain-Specific Development Standards

### 3.1. Bounded Context Implementation
Each bounded context MUST follow this structure:
```
src/[context_name]/
  __init__.py
  domain.py      # Domain models and value objects
  schemas.py     # Pydantic models for API boundaries
  repository.py  # Database access layer
  service.py     # Business logic and orchestration
  events.py      # Domain events
  commands.py    # Command handlers
  queries.py     # Query handlers
  projections.py # Event projections (if applicable)
  tests/
    test_domain.py
    test_service.py
    test_integration.py
    test_properties.py
```

### 3.2. Color Space Operations
All color operations MUST use CIELCh:
-   Store colors as `{L: float, C: float, h: float}`.
-   Use Delta E 2000 for perceptual color differences.
-   Document all color harmony calculations with mathematical formulas.

### 3.3. Event-Driven Standards
-   **Publishing:** Use the transactional outbox pattern. Events are immutable, versioned, and include `event_id`, `occurred_at`, `aggregate_id`, etc.
-   **Consumption:** Consumers MUST be idempotent. Monitor projector lag and alert if it exceeds 30 seconds.

### 3.4. Scoring System Implementation
-   **Hard Constraints:** Checked first in beam search. A violation immediately prunes the path. Zero tolerance for violations in production.
-   **Soft Scoring:** Functions return a normalized score [0, 1] and an explanation string. They must be pure and deterministic.

### 3.5. Coordinated Sets (Co-ords) Handling
-   Always check `set_cohesion_policy` before replacement.
-   Implement and test cascade planning for `strict` and `prefer_strict` policies.

## 4. Quantifiable Quality Gates

### 4.1. General Code Health
-   **Test Coverage:** Must be **95% or higher**. Commits must not decrease coverage.
-   **Linting & Typing:** Must pass `ruff` and `mypy` with **zero errors**.
-   **Code Complexity:** Cyclomatic complexity of any function must not exceed **10** (`radon`).
-   **Anti-Patterns:** Code must be free of anti-patterns as defined in **The Hitchhiker's Guide to Python**.

### 4.2. Project-Specific Performance Testing
-   **Benchmark Suite:** Every PR must run performance benchmarks.
-   **P95 Targets:** Generation ≤400ms, Replace ≤600ms.
-   **Load Testing:** System must handle 100 concurrent requests.

### 4.3. Project-Specific Correctness Testing
-   **Determinism:** Same inputs must produce identical outputs across 100 runs.
-   **Domain Invariants:** Tests must enforce layering order, one-piece exclusivity, group integrity for co-ords, and formality bounds.
-   **Integration Scenarios:** End-to-end tests are required for outfit generation, slot replacement with cascades, event projections, cache invalidation, and graceful degradation.

### 4.4. Property-Based Testing (Hypothesis)
Property-based tests are mandatory for complex logic. Each BC must have property tests, including:
-   **Wardrobe/Catalog:** Role-attribute consistency, color space bounds.
-   **Recommendation:** Deterministic generation, cohesion policy enforcement.

## 5. Task Implementation Workflow

Follow this multi-persona workflow for every task.

### Phase 0: Domain Understanding
Before planning, ensure complete understanding of fashion terminology, CIELCh, beam search, and CQRS patterns.

### Phase 1: Product Analysis (Product Manager Persona)
Define the "what" and "why" of the task, user stories, and acceptance criteria in a temporary `product_brief_temp.md`.

### Phase 2: Developer Briefing (Technical Lead Persona)
Outline the technical approach, challenges, and affected codebase areas in a `brief_temp.md`.

### Phase 3: Granular Planning (Senior Developer Persona)
Create a detailed, step-by-step checklist in a `todo_temp.md`.

### Phase 4: Implementation & Verification (Senior Python Developer Persona)
Execute the plan from `todo_temp.md`, adhering strictly to TDD. Continuously verify with quality checks.

### Phase 5: Performance Optimization
After implementation, profile to identify bottlenecks, apply optimizations (caching, query tuning), and verify P95 targets are met.

### Phase 6: Observability Setup
Implement required metrics, distributed tracing, and structured logging.

### The Code Review Scorecard
This scorecard must be completed and included in the body of every commit message.
```markdown
### Code Review Scorecard
- [ ] **Workflow Adherence:** The full multi-persona workflow was followed.
- [ ] **TDD Compliance:** A failing test was committed before each implementation part.
- [ ] **Test Coverage:** All new code is covered, and overall coverage is >=95%.
- [ ] **Code Health:** All quality gates (`ruff`, `mypy`, `radon`) pass.
- [ ] **Performance:** Performance benchmarks pass and P95 targets are met.
- [ ] **Documentation:** Docstrings are complete and `README.md` is updated.
```

## 6. Project-Specific Guidelines

### 6.1. Anti-Patterns to Avoid
-   **Color Space Mixing:** Convert all colors to L*C*h° at boundaries.
-   **Synchronous Event Processing:** Use transactional outbox with async workers.
-   **Unbounded Beam Search:** Enforce strict beam width and depth limits.
-   **Ignoring Confidence Scores:** Propagate confidence from inferred attributes through the scoring functions.

### 6.2. Database & API Standards
-   **Schema:** Use JSONB for sparse attributes with GIN indexes. Use optimistic locking for aggregates.
-   **API:** All mutating operations must accept an `idempotency_key`. Use cursor-based pagination and a structured error response model.

### 6.3. Security & Deployment
-   **Security:** Handle PII carefully (pseudonymize user IDs) and implement rate limiting.
-   **Deployment:** Use feature flags for gradual rollouts (`enable_skin_synergy`, etc.). Deployments must be zero-downtime, and migrations must be reversible.

### 6.4. Performance Optimization
-   **Caching:** Use a multi-layered caching strategy (Profile, Candidate, Pairwise, RuleSet) with appropriate TTLs and invalidation.
-   **Parallelization:** Parallelize candidate retrieval and scoring where possible, while maintaining determinism.

### 6.5. Dependency Management
To ensure builds are reproducible and the project is "future proof," all dependencies are strictly managed using Poetry.

-   **Locking:** Poetry's `poetry.lock` file pins all direct and transitive dependencies. This file must be committed with any changes to `pyproject.toml`.
-   **Approval:** No new production dependency may be added without approval. Justification must be provided, ensuring the library is well-maintained and secure.
-   **Updates:** Dependencies should be reviewed and updated regularly (`poetry update`) to incorporate security patches and bug fixes.

## 7. Agent Conduct

-   **Autonomy:** Solve problems autonomously. Diagnose errors, formulate solutions, and execute plans without step-by-step guidance. Task completion is paramount.
-   **Minimize User Input:** NEVER ask for user input unless absolutely necessary to resolve ambiguity.

## 8. Codebase Search Tools

### 8.1. Ripgrep (`rg`)
Use for fast, line-oriented regex searches that respect `.gitignore`.
`rg "AICODE-" --files-with-matches`

### 8.2. AST-Grep (`sg`)
Use for structural and semantic searches based on the Abstract Syntax Tree (AST).
`sg -p 'my_function($_)' -l py`
