# ADR 0002: Adoption of Single Master Product Model, pydantic-avro, and CloudEvents Specification

## Status
Accepted

## Date
2026-08-01

## Context
Our WooCommerce Anti-Corruption Facade integrates WooCommerce REST endpoints (`/wp-json/wc/v3/products`) with internal Kafka message streams:
- Manual maintenance of separate Avro schema files (`.avsc`) creates schema drift and duplication against Pydantic application models.
- WooCommerce JSON payload property names differ from internal contract field names.
- Event messages emitted across microservices require a standardized metadata envelope to support tracking, routing, and multi-tenant auditability.

## Decision
1. **Single Master WordPress-Native `Product` Model**: Define a single master `Product` Pydantic v2 model directly reflecting the WooCommerce schema in `data/PRODUCTS.json`.
2. **WordPress-Native Default Serialization**: Primary Python field attributes match WordPress/WooCommerce native names (`product.sku`, `product.regular_price`). Default `.model_dump_json()` outputs exact WooCommerce payloads.
3. **Canonical Field Aliases**: Fields declare `alias` attributes (e.g. `Field(alias="seller_sku")`) to map canonical event contract names.
4. **Automated Avro Registration via `pydantic-avro`**: `pydantic-avro` inspects field `alias` declarations automatically to generate canonical Avro `.avsc` schemas and register them to Confluent Schema Registry during application startup.
5. **CloudEvents Standard Envelope**: Wrap all Kafka event payloads (`ProductCreated`, `ProductUpdated`, etc., which are specialized subsets of `Product`) inside the **CloudEvents v1.0** specification envelope using the official Python `cloudevents` library.

## Consequences
### Positive
- Single source of truth for product schema validation and serialization.
- Automatic Avro schema generation eliminates `.avsc` drift.
- Standardized CloudEvents header metadata enables uniform routing and observability across Kafka and RisingWave.

### Negative
- Requires `pydantic-avro` and `cloudevents` Python library dependencies.
- Event consumers must unpack the CloudEvents envelope `data` attribute.
