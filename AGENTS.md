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

Every task, from a new feature to a bug fix, MUST follow this structured, multi-persona workflow. This ensures that work is thoroughly understood, planned, documented, and executed to the highest standard. The use of `AICODE-` comment prefixes is mandatory throughout this process.

### Phase 0: Domain Understanding & Initial Scoping
Before any planning documents are created, a foundational understanding must be established.
1.  **Objective:** Absorb the core concepts relevant to the task.
2.  **Actions:**
    *   Review the project `README.md` and `AGENTS.md` (this document).
    *   Study the specific domain model, including fashion terminology (Fashionpedia), color science (CIELCh), algorithms (beam search), and architecture (CQRS).
    *   Use codebase search tools (`rg`, `sg`) to identify existing code related to the task. **Crucially, search for existing `AICODE-` comments** (`rg "AICODE-"`) to understand previous developer intent, pending tasks, or important notes.

### Phase 1: Product Analysis (Product Manager Persona)
Define the "what" and the "why" of the task.
1.  **Objective:** Frame the problem from a user and business perspective.
2.  **Actions:**
    *   Create a temporary file named `product_brief_temp.md`.
    *   In this file, clearly define:
        *   **User Stories:** Who are the users and what do they want to achieve?
        *   **Acceptance Criteria:** How will we know when the feature is complete and correct?
        *   **Business Goal:** Why is this task important for the product?

### Phase 2: Developer Briefing (Technical Lead Persona)
Translate the product requirements into a high-level technical strategy.
1.  **Objective:** Outline a feasible technical approach.
2.  **Actions:**
    *   Create a temporary file named `brief_temp.md`.
    *   In this file, outline:
        *   **Proposed Solution:** A high-level description of the implementation.
        *   **Affected Systems:** Which Bounded Contexts, modules, or services will be touched?
        *   **Potential Challenges & Risks:** What are the known unknowns or potential blockers?

### Phase 3: Granular Planning (Senior Developer Persona)
Break down the high-level strategy into an executable, step-by-step plan.
1.  **Objective:** Create a detailed checklist that a junior developer could follow.
2.  **Actions:**
    *   Create a temporary file named `todo_temp.md`.
    *   Break down the technical brief into an extremely granular list of actions. Each item should be a small, verifiable change.
    *   **Incorporate `AICODE-` planning:** For complex logic, add steps in your `todo_temp.md` to first write out the plan using `AICODE-PSEUDO` or `AICODE-MATH` comments directly in the target source file before writing the actual code.

### Phase 4: Implementation & Verification (Senior Python Developer Persona)
Execute the plan with discipline and continuous verification. This is the core coding phase.
1.  **Objective:** Implement the solution according to the plan, adhering to all quality standards.
2.  **Actions:**
    *   **Search First:** Before modifying any file, search it again for any `AICODE-` comments that provide context or constraints.
    *   **Execute the Plan:** Follow your `todo_temp.md` step-by-step.
    *   **TDD Cycle:** Adhere strictly to the "Red-Green-Refactor" cycle for all code changes.
    *   **Document As You Go:** This is critical. **Use `AICODE-` comments extensively** to document your process *in the code itself*.
        *   Use `AICODE-NOTE` to explain a tricky part of the code or an assumption you made.
        *   Use `AICODE-TODO` to mark something that needs to be revisited.
        *   Write `AICODE-PSEUDO` or `AICODE-MATH` blocks *before* implementing their corresponding logic. This serves as your implementation blueprint.
    *   **Continuous Verification:** After each significant change, run the quality gates:
        *   Tests & Coverage: `coverage run -m pytest && coverage report`
        *   Code Health: `ruff check . && mypy . && radon cc . -a -nc`

### Phase 5: Performance Optimization
After the feature is functionally complete, ensure it meets performance SLOs.
1.  **Objective:** Validate and optimize the performance of the new code.
2.  **Actions:**
    *   **Profile:** Run the performance benchmark suite to identify any new bottlenecks.
    *   **Optimize:** Apply targeted optimizations (e.g., query tuning, caching, algorithmic improvements).
    *   **Verify:** Re-run benchmarks to confirm that P95 latency targets are met without introducing regressions.

### Phase 6: Observability Setup
Ensure the new feature is monitorable and supportable in production.
1.  **Objective:** Instrument the code for effective monitoring and debugging.
2.  **Actions:**
    *   **Metrics:** Add or update metrics for key operations (e.g., latency, error rates, bundle_found_rate).
    *   **Tracing:** Ensure new operations are included in the distributed trace by adding relevant spans.
    *   **Logging:** Add structured logs for important events, decisions, or errors.

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
