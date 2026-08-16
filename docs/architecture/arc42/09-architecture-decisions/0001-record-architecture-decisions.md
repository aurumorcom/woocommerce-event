# ADR 0001: Adoption of Asymmetric Integration System Pattern for WordPress Facade

## Status
Accepted

## Date
2026-08-01

## Context
Interfacing directly with third-party WordPress/WooCommerce instances introduces severe architectural coupling:
- WordPress uses relational database schemas (`wp_posts`, `wp_postmeta`) that do not match internal domain concepts.
- Synchronous HTTP requests during web checkout or inventory updates risk thread exhaustion and timeouts.
- Out-of-order events (e.g. order arriving before product creation completes) cause application crashes when handled synchronously in application code.

## Decision
We adopt the **Asymmetric Integration System Pattern on Windmill**:
1. Isolate WooCommerce behind a physical Anti-Corruption Facade implemented as stateless Windmill scripts.
2. Leverage Windmill as the workflow orchestrator and execution engine.
3. Use Confluent Schema Registry with `pydantic-avro` for automated Avro schema generation and registration.
4. Enforce Pydantic v2 master model parsing and CloudEvents v1.0 encapsulation across all inbound and outbound message streams.
5. Programmatically self-register stream topologies (`CREATE SOURCE`, `WATERMARK`, `CREATE MATERIALIZED VIEW`, `CREATE SINK`) on RisingWave.
6. Offload all stateful normalization, watermarking, out-of-order event gating, and idempotency checks to the RisingWave streaming SQL engine.
7. Dispatch normalized events from RisingWave to Windmill via HTTP Push Sinks with acknowledgment events published back to Kafka topics.

## Consequences
### Positive
- Zero leakage of WordPress/WooCommerce proprietary logic into core domain services.
- Eliminates application-level `time.sleep()` polling loops and local facade databases.
- Guarantees eventual consistency and multi-tenant isolation.

### Negative
- Requires operational management of Kafka, Schema Registry, and RisingWave cluster instances.
