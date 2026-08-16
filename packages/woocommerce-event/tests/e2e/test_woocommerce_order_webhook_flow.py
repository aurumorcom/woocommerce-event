"""E2E Test: Order Webhook Ingress -> Signature Validation -> CloudEvent Mapping -> Kafka Publication."""

import base64
import hashlib
import hmac
import json

import pytest
from fixtures.woocommerce_api_samples import SAMPLE_ORDER_RAW
from woocommerce_event.client import WooCommerceEventClient
from woocommerce_event.modules.orders.service import parse_order_webhook
from woocommerce_event.modules.webhooks.service import (
    validate_webhook_hmac_signature,
)


@pytest.mark.asyncio
async def test_order_webhook_ingress_e2e_flow():
    """Test receiving webhook payload, verifying HMAC, mapping to CloudEvent, and dispatching."""
    secret = "wc_webhook_secret_key_123"
    raw_payload_bytes = json.dumps(SAMPLE_ORDER_RAW).encode("utf-8")

    # Generate valid signature
    digest = hmac.new(
        secret.encode("utf-8"), raw_payload_bytes, hashlib.sha256
    ).digest()
    sig_header = base64.b64encode(digest).decode("utf-8")

    # 1. Validate signature
    is_valid = validate_webhook_hmac_signature(raw_payload_bytes, sig_header, secret)
    assert is_valid is True

    # 2. Parse into CloudEvent
    event = parse_order_webhook(SAMPLE_ORDER_RAW, tenant_id=1, site_id=101)
    assert event.type == "sales-order.created"
    assert event.subject == "101"
    assert event.tenant_id == 1
    assert event.data.id == 1001

    # 3. Publish to Kafka
    async with WooCommerceEventClient() as client:
        resp = await client.publish_event(topic="sales-order", event=event)
        assert resp.topic == "sales-order"
        assert resp.partition_key == "1"
