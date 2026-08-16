# 4. Solution Strategy

## 4.1 Key Architecture Decisions

### 1. Fully Asynchronous Physical Anti-Corruption Facade on Windmill
- **Strategy**: Isolate all WordPress/WooCommerce proprietary data formats and REST endpoints behind dedicated Windmill scripts in `apps/wordpress-kafka-api`. The codebase utilizes async network clients (`httpx.AsyncClient`) and `tenacity` for retries.
- **Rationale**: Prevents thread/worker exhaustion and provides robust handling of transient API failures without blocking event loops.

### 2. Windmill Script Execution & Native Event Handling
- **Strategy**: Windmill acts as the execution engine and script orchestrator. Inbound webhooks are parsed via Pydantic models imported from `packages/wordpress-kafka` and published directly to Kafka as Avro CloudEvents. Outbound requests are received from RisingWave HTTP Push Sinks, executed against WooCommerce REST endpoints, and acknowledged back to Kafka.
- **Rationale**: Eliminates separate polling workers or local databases in the facade, using Windmill's native execution state and retry mechanisms.

### 3. Offloading Event Gating to RisingWave
- **Strategy**: Define stateful JOIN Materialized Views with `WATERMARK FOR event_time` inside RisingWave streaming SQL engine. RisingWave fully manages idempotency, normalisation, and watermarking.
- **Rationale**: Eliminates `time.sleep()` polling loops and application-level gating in worker threads, keeping Windmill execution scripts 100% stateless.

### 4. Push-Based Event Ingestion
- **Strategy**: RisingWave streams events to downstream receivers via HTTP Push Sinks (`connector='http'`).
- **Rationale**: Converts pull-based consumer loops into uniform HTTP POST endpoints that can be load-balanced behind standard proxies.

### 5. Domain Models & `pydantic-avro` Schema Derivation
- **Strategy**: The microservice is structured around 7 core models: `Product`, `Category`, `Tag`, `Attribute`, `Media`, `Order`, and `Site`. The `Product` model directly represents the WooCommerce schema from `data/PRODUCTS.json`. Primary field names match WordPress attributes (`product.sku`, `product.regular_price`). Fields declare aliases (`alias="seller_sku"`) for canonical streams. `pydantic-avro` inspects field `alias` declarations automatically to generate canonical `.avsc` schemas.

### 6. Automated Tenant Webhook Self-Provisioning
- **Strategy**: When a user configures a tenant `Site` in Payload CMS, a `SiteCreated` event is published to Kafka. The Event Bridge consumes this event and calls the target WooCommerce REST API (`POST /wp-json/wc/v3/webhooks`) to automatically provision inbound webhooks.
- **Rationale**: Completely automates tenant store onboarding without requiring manual webhook configuration in WordPress admin dashboards.

### 7. CloudEvents Standard Encapsulation
- **Strategy**: Wrap all Kafka event payloads inside the CloudEvents v1.0 specification standard using the official Python `cloudevents` library (`specversion`, `id`, `source`, `type`, `datacontenttype`, `time`, `data`). Event variants (`ProductCreated`, `ProductUpdated`) inherit as specialized subsets of the master `Product` model.
- **Rationale**: Guarantees standard event metadata across multi-service topologies and third-party integrations.

### 8. Monorepo Architecture & Modular `src` Layout
- **Strategy**: Maintain a strict separation between shared domain libraries (`packages/wordpress-kafka`) and execution scripts (`apps/wordpress-kafka-api`). The core package adopts a feature-based modular `src/` layout (`src/wordpress_kafka/modules/{products,orders,sites}`) exposing schemas, service logic, and WooCommerce API clients. Windmill scripts in `apps/wordpress-kafka-api` act purely as thin execution shells (Imperative Shell) importing feature modules from `packages/wordpress-kafka` (Functional Core).
- **Rationale**: Enables fast unit testing with standard `pytest` without invoking web servers or Windmill daemons, eliminates code duplication across scripts, and avoids heavy web framework dependencies.
