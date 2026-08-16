"""Unit tests for webhook service functions."""

import base64
import hashlib
import hmac

import httpx
import pytest
from fixtures.woocommerce_api_samples import SAMPLE_WEBHOOK_RAW
from woocommerce_event.integrations.woocommerce import WooCommerceClient
from woocommerce_event.modules.webhooks.service import (
    parse_webhook_payload,
    provision_webhooks,
    validate_webhook_hmac_signature,
)


def test_validate_webhook_hmac_signature():
    """Test HMAC-SHA256 signature verification."""
    secret = "my_secret_key"
    payload = b'{"id": 123, "action": "test"}'
    digest = hmac.new(secret.encode(), payload, hashlib.sha256).digest()
    valid_sig = base64.b64encode(digest).decode()

    assert validate_webhook_hmac_signature(payload, valid_sig, secret) is True
    assert validate_webhook_hmac_signature(payload, "invalid_sig", secret) is False
    assert validate_webhook_hmac_signature(payload, "", "") is False


def test_parse_webhook_payload():
    """Test parsing webhook subscription into CloudEvent."""
    event = parse_webhook_payload(SAMPLE_WEBHOOK_RAW, tenant_id=1, site_id=101)
    assert event.type == "woocommerce.webhook.created"
    assert event.subject == "101"
    assert event.tenant_id == 1
    assert event.data.id == 10
    assert event.data.topic == "order.created"


@pytest.mark.asyncio
async def test_provision_webhooks():
    """Test provisioning webhooks via WooCommerceClient."""
    mock_transport = httpx.MockTransport(
        lambda req: httpx.Response(201, json=SAMPLE_WEBHOOK_RAW)
    )
    async with httpx.AsyncClient(transport=mock_transport) as http_client:
        client = WooCommerceClient(
            "https://store.example.com",
            "ck_test",
            "cs_test",
            client=http_client,
        )
        results = await provision_webhooks(
            client=client,
            delivery_url="https://api.example.com/wc",
            secret="whsec_123",
            topics=["product.created", "order.created"],
        )
        assert len(results) == 2
