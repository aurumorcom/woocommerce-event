"""Unit tests for tag service functions."""

import httpx
import pytest
from fixtures.woocommerce_api_samples import SAMPLE_TAG_RAW
from woocommerce_event.integrations.woocommerce import WooCommerceClient
from woocommerce_event.modules.tags.schemas import Tag
from woocommerce_event.modules.tags.service import (
    parse_tag_webhook,
    upsert_tag,
)


def test_parse_tag_webhook():
    """Test parsing tag webhook into CloudEvent."""
    event = parse_tag_webhook(
        raw_json=SAMPLE_TAG_RAW,
        tenant_id=1,
        site_id=101,
        action="created",
    )
    assert event.type == "item-tag.created"
    assert event.subject == "101"
    assert event.tenant_id == 1
    assert event.data.id == 22
    assert event.data.name == "Summer"


@pytest.mark.asyncio
async def test_upsert_tag():
    """Test upserting tag via WooCommerceClient."""
    mock_transport = httpx.MockTransport(
        lambda req: httpx.Response(201, json=SAMPLE_TAG_RAW)
    )
    async with httpx.AsyncClient(transport=mock_transport) as http_client:
        client = WooCommerceClient(
            "https://store.example.com",
            "ck_test",
            "cs_test",
            client=http_client,
        )
        tag = Tag(name="Winter")
        result = await upsert_tag(client, tag)
        assert result["id"] == 22
