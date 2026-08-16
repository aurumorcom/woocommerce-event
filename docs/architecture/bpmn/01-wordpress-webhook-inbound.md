# BPMN Workflow: WordPress Inbound Webhook Processing

This workflow models the inbound event ingestion when WordPress/WooCommerce triggers a webhook notification to the Windmill script endpoint, which validates, transforms, and publishes the event to Apache Kafka topic `product`.

```mermaid
flowchart TD
    Start[WordPress Webhook Event Triggered] --> Recv[Windmill Inbound Script Endpoint]
    Recv --> Trans[Parse Payload with Master Product Pydantic Model]
    
    Trans --> CloudEventsWrap[Wrap CDM in CloudEvents v1.0 Envelope]
    CloudEventsWrap --> AvroSerialize[Serialize to Binary Avro via pydantic-avro Schema]
    AvroSerialize --> KafkaPub[Push Serialized Event to Kafka Topic: product]
    KafkaPub --> Ack[Return HTTP 200 OK to WordPress]
```
