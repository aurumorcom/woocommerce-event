"""Unit tests for attribute service functions."""

import httpx
import pytest
from fixtures.woocommerce_api_samples import (
    SAMPLE_ATTRIBUTE_RAW,
    SAMPLE_ATTRIBUTE_TERM_RAW,
)
from woocommerce_event.integrations.woocommerce import WooCommerceClient
from woocommerce_event.modules.attributes.schemas import (
    Attribute,
    AttributeTerm,
)
from woocommerce_event.modules.attributes.service import (
    parse_attribute_term_webhook,
    parse_attribute_webhook,
    upsert_attribute,
    upsert_attribute_term,
)


def test_parse_attribute_webhooks():
    """Test parsing attribute and attribute term webhooks into CloudEvents."""
    event_attr = parse_attribute_webhook(SAMPLE_ATTRIBUTE_RAW, tenant_id=1, site_id=101)
    assert event_attr.type == "item-attribute.created"
    assert event_attr.subject == "101"
    assert event_attr.tenant_id == 1
    assert event_attr.data.id == 1

    event_term = parse_attribute_term_webhook(
        SAMPLE_ATTRIBUTE_TERM_RAW,
        attribute_id=1,
        tenant_id=1,
        site_id=101,
    )
    assert event_term.type == "item-attribute-value.created"
    assert event_term.subject == "101"
    assert event_term.tenant_id == 1
    assert event_term.data.id == 31


@pytest.mark.asyncio
async def test_upsert_attribute_and_term():
    """Test upserting attribute and term via WooCommerceClient."""

    def handler(request: httpx.Request) -> httpx.Response:
        if "terms" in str(request.url):
            return httpx.Response(201, json=SAMPLE_ATTRIBUTE_TERM_RAW)
        return httpx.Response(201, json=SAMPLE_ATTRIBUTE_RAW)

    mock_transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=mock_transport) as http_client:
        client = WooCommerceClient(
            "https://store.example.com",
            "ck_test",
            "cs_test",
            client=http_client,
        )
        attr = Attribute(name="Color")
        res_attr = await upsert_attribute(client, attr)
        assert res_attr["id"] == 1

        term = AttributeTerm(name="Blue")
        res_term = await upsert_attribute_term(client, 1, term)
        assert res_term["id"] == 31
