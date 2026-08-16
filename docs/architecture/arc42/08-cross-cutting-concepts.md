# 8. Cross-Cutting Concepts

## 8.1 Data Validation & Auto-Derived Schemas
Incoming data from WooCommerce webhooks is untrusted and must be rigorously validated at the ingress boundary. Windmill scripts achieve this by parsing payloads into strictly typed `Pydantic v2` models located in `packages/wordpress-kafka/src/wordpress_kafka/modules/`. Once validated, payloads are serialized using `.avsc` schemas auto-derived from the Pydantic classes via `pydantic-avro`.

## 8.2 Stream Idempotency & Deduplication
To prevent duplicate state transitions during retries or network splits:
- The facade scripts inside `apps/wordpress-kafka-api` remain **completely stateless**.
- All stream-level idempotency checks, deduplication windows, normalization, and watermarking are entirely delegated to **RisingWave Materialized Views**. RisingWave uses the `tenant_id` and unique `entity_id` payload components to discard repeated events before they can trigger outbound WooCommerce REST calls.

## 8.3 Rate Limiting & API Backoff
WooCommerce REST APIs frequently enforce rate limits. Windmill outbound scripts use `tenacity` to apply **Exponential Backoff with Jitter** when catching `HTTP 429 Too Many Requests` or `HTTP 502/503/504` transient failures, ensuring fair usage of external API limits.

## 8.4 Observability
- **Standardized Context**: All logs emitted by `packages/wordpress-kafka` utils carry the `tenant_id` and `event_id` metadata.
- **Traceability**: CloudEvents headers trace the origin (`source`) and mutation of every event through the Kafka pipeline.
