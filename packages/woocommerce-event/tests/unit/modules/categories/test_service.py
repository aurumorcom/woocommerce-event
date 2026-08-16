"""Unit tests for category service functions."""

import httpx
import pytest
from fixtures.woocommerce_api_samples import SAMPLE_CATEGORY_RAW
from woocommerce_event.integrations.woocommerce import WooCommerceClient
from woocommerce_event.modules.categories.schemas import Category
from woocommerce_event.modules.categories.service import (
    parse_category_webhook,
    upsert_category,
)


def test_parse_category_webhook():
    """Test parsing category webhook into CloudEvent."""
    event = parse_category_webhook(
        raw_json=SAMPLE_CATEGORY_RAW,
        tenant_id=1,
        site_id=101,
        action="created",
    )
    assert event.type == "item-category.created"
    assert event.subject == "101"
    assert event.tenant_id == 1
    assert event.data.id == 15
    assert event.data.name == "Clothing"


@pytest.mark.asyncio
async def test_upsert_category():
    """Test upserting category via WooCommerceClient."""
    mock_transport = httpx.MockTransport(
        lambda req: httpx.Response(201, json=SAMPLE_CATEGORY_RAW)
    )
    async with httpx.AsyncClient(transport=mock_transport) as http_client:
        client = WooCommerceClient(
            "https://store.example.com",
            "ck_test",
            "cs_test",
            client=http_client,
        )
        cat = Category(name="Shoes")
        result = await upsert_category(client, cat)
        assert result["id"] == 15
