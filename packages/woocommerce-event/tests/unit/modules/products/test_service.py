"""Unit tests for product service functions."""

import httpx
import pytest
from fixtures.woocommerce_api_samples import SAMPLE_PRODUCT_RAW
from woocommerce_event.integrations.woocommerce import WooCommerceClient
from woocommerce_event.modules.products.schemas import Product
from woocommerce_event.modules.products.service import (
    parse_product_webhook,
    upsert_product,
)


def test_parse_product_webhook():
    """Test parsing product webhook into CloudEvent."""
    event = parse_product_webhook(
        raw_json=SAMPLE_PRODUCT_RAW,
        tenant_id=1,
        site_id=101,
        action="created",
    )
    assert event.type == "product.created"
    assert event.subject == "101"
    assert event.tenant_id == 1
    assert event.data.id == 799
    assert event.data.sku == "TSHIRT-PREM"


@pytest.mark.asyncio
async def test_upsert_product():
    """Test upserting product via WooCommerceClient."""
    mock_transport = httpx.MockTransport(
        lambda req: httpx.Response(201, json=SAMPLE_PRODUCT_RAW)
    )
    async with httpx.AsyncClient(transport=mock_transport) as http_client:
        client = WooCommerceClient(
            "https://store.example.com",
            "ck_test",
            "cs_test",
            client=http_client,
        )
        product = Product(name="New Product", sku="PROD-NEW")
        result = await upsert_product(client, product)
        assert result["id"] == 799
