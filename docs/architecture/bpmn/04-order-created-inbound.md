# BPMN Workflow: Inbound Order Created Workflow

This workflow models inbound order notifications initiated by WooCommerce webhooks when a customer places an order, publishing the canonical event directly to Apache Kafka topic `sales.order`.

```mermaid
flowchart TD
    WCOrder[WooCommerce woocommerce_new_order Webhook] --> WindmillIngress[Windmill Inbound Order Script Endpoint]
    
    WindmillIngress --> OrderTrans[Translate WooCommerce Order Schema to Avro CDM]
    OrderTrans --> CloudEventsWrap[Wrap in CloudEvents v1.0 Envelope]
    CloudEventsWrap --> KafkaPub[Publish to Kafka Topic: sales.order]
```
