# 6. Runtime View

## 6.1 Event Workflows & Execution Paths
The system runtime scenarios are documented in individual BPMN workflow files under [`docs/architecture/bpmn/`](../bpmn/):

1. **Inbound WordPress Webhook Processing**: [`bpmn/01-wordpress-webhook-inbound.md`](../bpmn/01-wordpress-webhook-inbound.md)
   - Receives raw webhook POSTs, translates payload to CDM, and publishes to Kafka topic `product`.

2. **Outbound Product Creation**: [`bpmn/02-product-created-outbound.md`](../bpmn/02-product-created-outbound.md)
   - Product event on Kafka topic `product` -> RisingWave execution of idempotency check, normalization, and watermarking -> Windmill script execution -> WooCommerce REST API `POST /wp-json/wc/v3/products` -> Status event published to Kafka topic `product`.

3. **Outbound Product Update**: [`bpmn/03-product-updated-outbound.md`](../bpmn/03-product-updated-outbound.md)
   - Product update event on Kafka topic `product` -> RisingWave idempotency check, normalization, and watermarking -> Windmill script execution -> WooCommerce REST API `PUT /wp-json/wc/v3/products/{id}`.

4. **Inbound Order Created**: [`bpmn/04-order-created-inbound.md`](../bpmn/04-order-created-inbound.md)
   - WooCommerce `woocommerce_new_order` webhook -> Windmill translation script -> Kafka topic `sales.order`.

5. **Outbound Inventory Synchronization**: [`bpmn/05-inventory-synced-outbound.md`](../bpmn/05-inventory-synced-outbound.md)
   - Stock update event on Kafka topic `stock.level` -> RisingWave idempotency check, normalization, and watermarking -> Windmill script execution -> WooCommerce REST API `PUT /wp-json/wc/v3/products/{id}` (`stock_quantity`).

6. **Automated Site & Webhook Self-Provisioning**: [`bpmn/06-site-provisioning.md`](../bpmn/06-site-provisioning.md)
   - Site event on Kafka topic `tenant` -> Windmill script execution -> WooCommerce REST API `POST /wp-json/wc/v3/webhooks` -> Webhook ID & secret stored in tenant config -> Lifecycle status updated on `tenant` topic.
