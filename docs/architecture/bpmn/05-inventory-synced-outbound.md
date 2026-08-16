# BPMN Workflow: Outbound Inventory Synchronization Workflow

This workflow models the real-time synchronization of stock levels and inventory quantities from Kafka topic `stock.level` to WooCommerce products. RisingWave performs idempotency check, normalization, and watermarking before triggering the Windmill script.

```mermaid
flowchart TD
    KafkaPub[Kafka Topic: stock.level] --> RWSource[RisingWave Ingestion Source WATERMARK FOR event_time]
    RWSource --> RWProcess{RisingWave Stream Engine: Idempotency Check, Normalization, Watermarking}
    RWProcess -->|Duplicate or Out of Order| RWDrop[Drop Event in RisingWave]
    
    RWProcess -->|Normalized Unique Event| RWMV[RisingWave Materialized View JOIN with Product Metadata]
    RWMV --> RWSink[RisingWave HTTP Push Sink POST to Windmill Script Endpoint]
    
    RWSink --> WindmillScript[Windmill Inventory Sync Script Execution]
    WindmillScript --> HttpClient[Async WooCommerce REST Call PUT /wp-json/wc/v3/products/id stock_quantity]
    
    HttpClient --> WPResp{WooCommerce PUT Response}
    WPResp -->|200 OK| StatusSuccess[Translate to InventorySynced Ack Status]
    WPResp -->|Non-200 Error| StatusFail[Translate to SyncError Ack Status]
    
    StatusSuccess --> KafkaStatus[Publish Ack Event to Kafka Topic: stock.level]
    StatusFail --> KafkaStatus
```
