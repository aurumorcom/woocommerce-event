"""Sample API responses for WooCommerce REST API endpoints."""

SAMPLE_PRODUCT_RAW = {
    "id": 799,
    "name": "Premium T-Shirt",
    "slug": "premium-t-shirt",
    "permalink": "https://store.example.com/product/premium-t-shirt/",
    "type": "variable",
    "status": "publish",
    "featured": False,
    "catalog_visibility": "visible",
    "description": "<p>High quality organic cotton shirt.</p>",
    "short_description": "<p>Organic cotton shirt.</p>",
    "sku": "TSHIRT-PREM",
    "price": "29.99",
    "regular_price": "29.99",
    "sale_price": "",
    "manage_stock": True,
    "stock_quantity": 42,
    "stock_status": "instock",
    "weight": "0.3",
    "dimensions": {"length": "10", "width": "8", "height": "1"},
    "images": [
        {
            "id": 101,
            "src": "https://store.example.com/wp-content/uploads/shirt.jpg",
            "name": "shirt",
            "alt": "Shirt Front",
        }
    ],
    "attributes": [
        {
            "id": 1,
            "name": "Size",
            "position": 0,
            "visible": True,
            "variation": True,
            "options": ["S", "M", "L"],
        }
    ],
    "categories": [{"id": 15, "name": "Clothing", "slug": "clothing"}],
    "tags": [{"id": 22, "name": "Summer", "slug": "summer"}],
    "variations": [801, 802, 803],
}

SAMPLE_VARIATION_RAW = {
    "id": 801,
    "parent_id": 799,
    "sku": "TSHIRT-PREM-M",
    "price": "29.99",
    "regular_price": "29.99",
    "sale_price": "",
    "status": "publish",
    "manage_stock": True,
    "stock_quantity": 15,
    "stock_status": "instock",
    "weight": "0.3",
    "dimensions": {"length": "10", "width": "8", "height": "1"},
    "image": {
        "id": 102,
        "src": "https://store.example.com/wp-content/uploads/shirt-m.jpg",
        "name": "shirt-m",
        "alt": "Size M",
    },
    "attributes": [{"id": 1, "name": "Size", "option": "M"}],
}

SAMPLE_ORDER_RAW = {
    "id": 1001,
    "parent_id": 0,
    "number": "1001",
    "order_key": "wc_order_abc123",
    "status": "processing",
    "currency": "USD",
    "date_created": "2025-01-15T12:00:00Z",
    "date_modified": "2025-01-15T12:05:00Z",
    "discount_total": "0.00",
    "discount_tax": "0.00",
    "shipping_total": "5.00",
    "shipping_tax": "0.50",
    "cart_tax": "2.50",
    "total": "37.99",
    "total_tax": "3.00",
    "customer_id": 42,
    "billing": {
        "first_name": "Jane",
        "last_name": "Doe",
        "company": "Acme Corp",
        "address_1": "123 Main St",
        "address_2": "Suite 4",
        "city": "Austin",
        "state": "TX",
        "postcode": "78701",
        "country": "US",
        "email": "jane@example.com",
        "phone": "555-0199",
    },
    "shipping": {
        "first_name": "Jane",
        "last_name": "Doe",
        "company": "Acme Corp",
        "address_1": "123 Main St",
        "address_2": "Suite 4",
        "city": "Austin",
        "state": "TX",
        "postcode": "78701",
        "country": "US",
    },
    "payment_method": "stripe",
    "payment_method_title": "Credit Card",
    "transaction_id": "ch_123456789",
    "line_items": [
        {
            "id": 501,
            "name": "Premium T-Shirt - M",
            "product_id": 799,
            "variation_id": 801,
            "quantity": 1,
            "tax_class": "",
            "subtotal": "29.99",
            "subtotal_tax": "2.50",
            "total": "29.99",
            "total_tax": "2.50",
            "sku": "TSHIRT-PREM-M",
            "price": 29.99,
        }
    ],
    "tax_lines": [
        {
            "id": 601,
            "rate_code": "TX-STATE",
            "rate_id": 1,
            "label": "State Tax",
            "compound": False,
            "tax_total": "2.50",
            "shipping_tax_total": "0.50",
        }
    ],
}

SAMPLE_CATEGORY_RAW = {
    "id": 15,
    "name": "Clothing",
    "slug": "clothing",
    "parent": 0,
    "description": "All clothing items",
    "display": "default",
    "image": {
        "id": 201,
        "src": "https://store.example.com/cat.jpg",
        "name": "cat",
        "alt": "Clothing",
    },
    "menu_order": 1,
    "count": 24,
}

SAMPLE_TAG_RAW = {
    "id": 22,
    "name": "Summer",
    "slug": "summer",
    "description": "Summer seasonal collection",
    "count": 8,
}

SAMPLE_ATTRIBUTE_RAW = {
    "id": 1,
    "name": "Size",
    "slug": "pa_size",
    "type": "select",
    "order_by": "menu_order",
    "has_archives": True,
}

SAMPLE_ATTRIBUTE_TERM_RAW = {
    "id": 31,
    "name": "Medium",
    "slug": "m",
    "description": "Medium size",
    "menu_order": 2,
    "count": 14,
}

SAMPLE_MEDIA_RAW = {
    "id": 101,
    "date": "2025-01-15T10:00:00",
    "slug": "shirt-front",
    "type": "attachment",
    "link": "https://store.example.com/shirt-front/",
    "title": {"rendered": "Shirt Front"},
    "author": 1,
    "source_url": "https://store.example.com/wp-content/uploads/shirt.jpg",
    "media_type": "image",
    "mime_type": "image/jpeg",
    "media_details": {
        "width": 1200,
        "height": 1200,
        "file": "2025/01/shirt.jpg",
        "filesize": 245100,
    },
}

SAMPLE_WEBHOOK_RAW = {
    "id": 10,
    "name": "Order Created Webhook",
    "status": "active",
    "topic": "order.created",
    "resource": "order",
    "event": "created",
    "hooks": ["woocommerce_new_order"],
    "delivery_url": "https://ingress.example.com/wc-webhook",
    "secret": "whsec_test123",
    "date_created": "2025-01-01T00:00:00Z",
}

SAMPLE_SYSTEM_STATUS_RAW = {
    "environment": {
        "home_url": "https://store.example.com",
        "site_url": "https://store.example.com",
        "version": "8.5.0",
        "wp_version": "6.4.2",
        "php_version": "8.2.14",
        "server_info": "nginx/1.24.0",
    },
    "database": {
        "wc_database_version": "8.5.0",
        "database_prefix": "wp_",
        "maxmind_geoip_database": "Installed",
    },
    "security": {
        "secure_connection": True,
        "hide_errors": True,
    },
    "settings": {
        "api_enabled": True,
        "currency": "USD",
    },
}
