# BPMN Workflow: Outbound Product Update Workflow

This workflow models the modification of existing WooCommerce product entities via `PUT /wp-json/wc/v3/products/{id}`. RisingWave performs idempotency check, normalization, and watermarking on Kafka topic `product` before triggering the Windmill script.

```mermaid
flowchart TD
    KafkaProd[Kafka Topic: product] --> RWIngest[RisingWave Ingestion Source]
    RWIngest --> RWProcess{RisingWave Stream Engine: Idempotency Check, Normalization, Watermarking}
    
    RWProcess -->|Duplicate or Superseded| RWDrop[Skip or Drop Event in RisingWave]
    RWProcess -->|Normalized Unique Event| RWSink[RisingWave HTTP Push Sink POST to Windmill Script Endpoint]
    RWSink --> WindmillScript[Windmill Outbound Sync Script Execution]
    
    WindmillScript --> HttpClient[Async WooCommerce REST Call PUT /wp-json/wc/v3/products/id]
    
    HttpClient --> WPResp{WooCommerce API Response}
    WPResp -->|200 OK| StatusSuccess[Translate to ProductUpdated Status Ack]
    WPResp -->|404 Not Found| StatusMissing[Translate to ProductNotFound Status Ack]
    WPResp -->|500 Error| StatusError[Translate to SyncError Status Ack]
    
    StatusSuccess --> StatusKafka[Publish Ack to Kafka Topic: product]
    StatusMissing --> StatusKafka
    StatusError --> StatusKafka
```
