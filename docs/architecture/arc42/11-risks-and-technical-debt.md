# 11. Risks and Technical Debt

## 11.1 Architectural Risks
1. **RisingWave State Store Growth**:
   - *Risk*: Retaining unbounded historical stream events in RisingWave materialized views for idempotency checks will bloat the state store.
   - *Mitigation*: Ensure explicit `WATERMARK` and temporal filters (e.g. `event_time > current_timestamp - interval '7 days'`) are applied to all deduplication queries to eagerly garbage-collect outdated state.

2. **WooCommerce Rate Limiting Collisions**:
   - *Risk*: Bulk product creations or inventory syncs can trigger global `HTTP 429` blocks on a target tenant store, affecting simultaneous normal operations.
   - *Mitigation*: Outbound Windmill scripts utilize `tenacity` for backoff, but extreme bulk operations might necessitate a dedicated, slower rate-limited queue topic.

## 11.2 Technical Debt
1. **Pydantic to Avro Edge Cases**:
   - *Current State*: `pydantic-avro` works for standard primitives, but complex nested WooCommerce JSON objects or union types might require manual mapping overrides.
   - *Future Enhancement*: Implement a custom schema registry interceptor or specific model validators to handle WooCommerce's edge-case payload inconsistencies.
