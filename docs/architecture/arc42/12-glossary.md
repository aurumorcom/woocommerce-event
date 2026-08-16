# 12. Glossary

| Term | Definition |
| :--- | :--- |
| **Windmill** | Developer platform and execution engine used to orchestrate and run stateless Python scripts and webhooks in response to external triggers. |
| **ACL (Anti-Corruption Layer)** | A design pattern that translates requests and responses between two subsystems with different domain models, preventing external schemas from polluting internal systems. |
| **CDM (Canonical Data Model)** | A standardized, framework-agnostic data format used across internal event topics and microservice communications. |
| **HTTP Push Sink** | A RisingWave output connector that actively dispatches query results to downstream HTTP endpoints as events are materialized. |
| **Watermarking** | A stream processing mechanism used by RisingWave to denote how far event time has progressed, allowing the engine to close windows and discard late-arriving data. |
| **RisingWave** | A cloud-native distributed SQL streaming database designed for stateful event joins, normalization, idempotency, and low-latency materialization. |
| **Apache Avro** | A compact binary serialization format providing rich data structures and schema evolution for Kafka event topics. |
| **Pydantic v2** | A Python data validation library using Rust underneath for fast type parsing, schema generation, and strict model enforcement. |
| **Schema Registry** | A centralized service providing a serving layer for event schemas (Avro) and enforcing compatibility rules across Kafka topics. |
| **WooCommerce** | An open-source e-commerce plugin for WordPress providing REST API endpoints (`/wp-json/wc/v3`) and webhook triggers. |
