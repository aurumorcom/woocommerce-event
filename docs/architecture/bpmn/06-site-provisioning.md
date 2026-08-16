# BPMN Workflow: Site Webhook Self-Provisioning Workflow

This workflow models the dynamic self-provisioning execution path when a site provisioning event is published to Kafka topic `tenant`. The **WordPress Kafka Event Bridge** consumes the event from Kafka and automatically provisions inbound webhooks on the tenant's remote WordPress site via the WooCommerce REST API (`POST /wp-json/wc/v3/webhooks`).

```mermaid
flowchart TD
    SiteEvent[Kafka Topic: tenant] --> WindmillScript[Windmill Site Provisioning Script Execution]
    
    WindmillScript --> ParseConfig[Parse Site Credentials: tenant_id, site_url, consumer_key, consumer_secret]
    
    ParseConfig --> GenSecret[Generate Unique HMAC SHA256 Webhook Secret]
    GenSecret --> ProvisionCall[Async REST Call to WooCommerce: POST /wp-json/wc/v3/webhooks]
    
    ProvisionCall --> WPApi{WooCommerce REST API Response}
    WPApi -->|201 Created| StoreConfig[Save Provisioned Webhook ID & Secret in Tenant Config Store]
    WPApi -->|4xx / 5xx Error| RetryCall[Retry with Exponential Backoff via Tenacity]
    RetryCall --> ProvisionCall
    
    StoreConfig --> AckSuccess[Publish SiteProvisioned Ack Event to Kafka Topic: tenant]
```
