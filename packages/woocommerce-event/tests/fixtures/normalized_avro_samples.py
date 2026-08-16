"""Sample CloudEvents and Avro normalized structures."""

SAMPLE_CLOUDEVENT_PRODUCT_CREATED = {
    "specversion": "1.0",
    "type": "product.created",
    "source": "woocommerce://101/products",
    "subject": "101",
    "id": "evt-prod-001",
    "time": "2025-01-15T12:00:00Z",
    "datacontenttype": "application/json",
    "data": {
        "id": 799,
        "name": "Premium T-Shirt",
        "sku": "TSHIRT-PREM",
        "price": "29.99",
    },
    "tenant_id": "1",
}

SAMPLE_CLOUDEVENT_ORDER_CREATED = {
    "specversion": "1.0",
    "type": "sales-order.created",
    "source": "woocommerce://101/orders",
    "subject": "101",
    "id": "evt-ord-001",
    "time": "2025-01-15T12:05:00Z",
    "datacontenttype": "application/json",
    "data": {
        "id": 1001,
        "number": "1001",
        "total": "37.99",
        "status": "processing",
    },
    "tenant_id": "1",
}
