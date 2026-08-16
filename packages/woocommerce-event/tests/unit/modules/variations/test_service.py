"""Unit tests for variation service functions."""

import httpx
import pytest
from fixtures.woocommerce_api_samples import SAMPLE_VARIATION_RAW
from woocommerce_event.integrations.woocommerce import WooCommerceClient
from woocommerce_event.modules.variations.schemas import Variation
from woocommerce_event.modules.variations.service import (
    parse_variation_webhook,
    upsert_variation,
)


def test_parse_variation_webhook():
    """Test parsing variation webhook into CloudEvent."""
    event = parse_variation_webhook(
        raw_json=SAMPLE_VARIATION_RAW,
        parent_id=799,
        tenant_id=1,
        site_id=101,
        action="created",
    )
    assert event.type == "product-variant.created"
    assert event.subject == "101"
    assert event.tenant_id == 1
    assert event.data.id == 801
    assert event.data.parent_id == 799


@pytest.mark.asyncio
async def test_upsert_variation():
    """Test upserting variation via WooCommerceClient."""
    mock_transport = httpx.MockTransport(
        lambda req: httpx.Response(201, json=SAMPLE_VARIATION_RAW)
    )
    async with httpx.AsyncClient(transport=mock_transport) as http_client:
        client = WooCommerceClient(
            "https://store.example.com",
            "ck_test",
            "cs_test",
            client=http_client,
        )
        variation = Variation(sku="TSHIRT-PREM-L")
        result = await upsert_variation(client, product_id=799, variation=variation)
        assert result["id"] == 801
