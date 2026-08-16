# BPMN Workflow: Outbound Product Creation Workflow

This workflow models the outbound execution path when a product creation event is consumed from Kafka topic `product` by RisingWave. RisingWave executes idempotency check, normalization, and watermarking before pushing the event to the Windmill script to create the product in WooCommerce via REST API.

```mermaid
flowchart TD
    OutboxPub[Kafka Topic: product] --> RWSafe[RisingWave Ingestion Source]
    RWSafe --> RWProcess{RisingWave Stream Engine: Idempotency Check, Normalization, Watermarking}
    
    RWProcess -->|Duplicate / Pending Prerequisites| RWState[Hold or Drop in RisingWave State Store]
    RWProcess -->|Normalized & Unique Event| RWSink[RisingWave HTTP Push Sink POST to Windmill Script Endpoint]
    
    RWSink --> WindmillScript[Windmill Outbound Sync Script Execution]
    WindmillScript --> PydanticParse[Parse Payload with Product Pydantic Model]
    PydanticParse --> HttpClient[Async WooCommerce REST Call POST /wp-json/wc/v3/products]
    
    HttpClient --> WPApi{WooCommerce REST API Response}
    WPApi -->|201 Created| SuccessTrans[Translate Response to ProductCreated Ack Status]
    WPApi -->|4xx / 5xx Error| FailTrans[Translate Response to SyncError Ack Status]
    
    SuccessTrans --> StatusPub[Publish Ack Event to Kafka Topic: product]
    FailTrans --> StatusPub
```
