# ADR 0004: Adoption of 3-Layer, 2-Repository Architecture

## Status
Accepted

## Date
2024-05-24

## Context
The project initially adopted a monorepo structure (ADR 0003) to combine core domain logic with execution-layer endpoints. As the complexity of the internal Kafka integration system grew—specifically regarding RisingWave SQL generation, schema registry synchronization, and stream topology auto-registration—it became clear that these infrastructure capabilities are highly reusable across other potential integrations (e.g., Shopify, Stripe). 

Keeping these generic infrastructure tools tightly coupled to the WordPress-specific domain logic within a single repository limits reusability and creates artificial dependencies.

## Decision
We will restructure the project into a **3-Layer, 2-Repository** architecture:

1. **Repository 1: `python-kafka` (Infrastructure SDK Layer)**
   - **Layer 1 (Streaming Platform Engine & DDL Synthesizer):** Handles Pydantic-to-Avro schema generation, Schema Registry synchronization, RisingWave SQL/DDL generation (`SOURCE`, `WATERMARK`, `MATERIALIZED VIEW`, `SINK`), service auto-provisioning, and idempotency/deduplication middleware. This repo contains zero WordPress-specific logic.

2. **Repository 2: `wordpress-kafka` (Domain Facade & Execution Layer)**
   - **Layer 2 (Domain Schemas & Anti-Corruption Translation):** Contains WordPress/WooCommerce canonical Pydantic schemas (`Product`, `Order`, `Category`) decorated with metadata recognized by `python-kafka`. Also includes the Anti-Corruption Layer (ACL) for translating webhooks.
   - **Layer 3 (Execution & API Integration):** Windmill execution shells (e.g., `products.py`) and WooCommerce REST client wrappers for handling inbound webhooks and outbound API calls.

## Consequences
### Positive
- **High Reusability:** The `python-kafka` SDK can be utilized by future microservices or external system facades without reinventing RisingWave integration or schema synchronization.
- **Strict Domain Isolation:** `wordpress-kafka` is solely focused on WordPress business logic, WooCommerce HTTP interactions, and domain modeling.
- **Independent Lifecycles:** Infrastructure updates (e.g., a new RisingWave connector version) can be released in `python-kafka` independently of WordPress domain changes.

### Negative
- **Dependency Management:** Requires proper cross-repository dependency management (e.g., via `pip` or Git submodules) so that `wordpress-kafka` can reliably import `python-kafka`.
- **Testing Complexity:** Integration testing across the boundary of the SDK and the Domain Facade requires pulling the `python-kafka` library into the test environment.
