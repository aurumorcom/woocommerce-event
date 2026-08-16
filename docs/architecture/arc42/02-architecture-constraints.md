# 2. Architecture Constraints

## 2.1 Technical Constraints
- **Framework & Runtime**: Python 3.11+ / Windmill Engine with Pydantic v2. The ENTIRE Python codebase MUST be fully asynchronous (`async`/`await` coroutines) when interacting with external networks. Blocking I/O or `time.sleep()` is STRICTLY FORBIDDEN. Fast API or other heavy web frameworks are FORBIDDEN in the execution layer.
- **Messaging Infrastructure**: Apache Kafka cluster paired with Confluent Schema Registry (Apache Avro specification).
- **Stream Processing**: RisingWave streaming SQL engine for stateful joins, normalization, watermarking, idempotency, and HTTP Push Sinks.
- **Third-Party API Protocol**: WooCommerce REST API `wc/v3` over HTTPS with OAuth 1.0a / Basic Authentication.

## 2.2 Operational & Regulatory Constraints
- **No Direct WordPress Database Access**: All interactions with WordPress MUST occur via HTTP REST endpoints or webhook receivers. Direct MySQL reads/writes to `wp_posts` or `wp_postmeta` are FORBIDDEN.
- **Multi-Tenant Context propagation**: Every payload MUST carry a `tenant_id` allowing downstream services or stream filters to correctly associate events with specific merchants/tenants.
- **At-Least-Once Delivery**: Systems MUST account for potential duplicate webhook deliveries by enforcing stream-level atomic idempotency checks in RisingWave prior to triggering external APIs.
