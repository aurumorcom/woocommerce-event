# ADR 0003: Adoption of Monorepo Layout with Core Tooling Package and Windmill Application Execution

## Status
Accepted

## Date
2026-08-01

## Context
The WordPress Kafka Event Bridge requires clean separation between core domain logic (Pydantic models, Avro schema generation, CloudEvents envelopes, WooCommerce REST client wrappers, and HMAC verification) and execution-layer endpoints (Windmill webhook scripts and RisingWave HTTP Push sink handlers):
- Inlining core domain logic inside individual Windmill scripts leads to code duplication, drift, and inability to run fast unit tests with standard `pytest`.
- Coupling execution logic to a heavy web framework adds unnecessary framework abstractions when Windmill natively provides HTTP endpoints, webhook triggers, and script orchestration.
- Modern Python standards favor feature-based modular `src/` package layouts (`src/wordpress_kafka/modules/...`) over flat or type-based directories.

## Decision
1. **Monorepo Workspace Layout**: Structure the project as a monorepo workspace containing `packages/` (shared libraries) and `apps/` (executable applications/workflows).
2. **Core Tooling Package (`packages/wordpress-kafka`)**: Encapsulate all domain models, CloudEvents wrappers, Schema Registry clients, WooCommerce API clients, and HMAC security validators inside a dedicated Python package adhering to a **modular `src/` layout**:
   - `src/wordpress_kafka/config/`: Application settings and environment parsing.
   - `src/wordpress_kafka/core/`: CloudEvents envelope wrappers and Schema Registry tools.
   - `src/wordpress_kafka/utils/`: HMAC verification, logging, and helpers.
   - `src/wordpress_kafka/modules/{products,orders,categories,tags,attributes,media,sites}/`: Feature-based domain modules containing `schemas.py`, `service.py`, and `client.py`.
3. **Execution Application (`apps/wordpress-kafka-api`)**: Organize all Windmill scripts under `apps/wordpress-kafka-api/f/wordpress-kafka/` (`products.py`, `orders.py`, `categories.py`, `tags.py`, `attributes.py`, `media.py`, `sites.py`). Windmill scripts act strictly as thin execution shells (Imperative Shell) that import feature modules from `packages/wordpress-kafka` (Functional Core).
4. **No Heavy Web Framework**: Eliminate standalone web framework dependencies in favor of Windmill's native HTTP webhook ingress and script execution engine.

## Consequences
### Positive
- Strict adherence to Functional Core, Imperative Shell pattern.
- High gear / low gear TDD: Core domain logic and schemas can be thoroughly tested using `pytest` without invoking Windmill or external HTTP servers.
- High reusability: Core library can be imported by CLI tools, background workers, or migration scripts.

### Negative
- Requires monorepo workspace configuration (`uv` workspace / `pdm`) to link package dependencies during local development and CI/CD builds.
- Requires installing `packages/wordpress-kafka` into Windmill worker runtime containers.
