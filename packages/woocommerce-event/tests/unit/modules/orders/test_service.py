"""Unit tests for order service functions."""

import httpx
import pytest
from fixtures.woocommerce_api_samples import SAMPLE_ORDER_RAW
from woocommerce_event.integrations.woocommerce import WooCommerceClient
from woocommerce_event.modules.orders.schemas import Order
from woocommerce_event.modules.orders.service import (
    fetch_order_details,
    parse_order_webhook,
    submit_order,
)


def test_parse_order_webhook():
    """Test parsing order webhook into CloudEvent."""
    event = parse_order_webhook(
        raw_json=SAMPLE_ORDER_RAW,
        tenant_id=1,
        site_id=101,
        action="created",
    )
    assert event.type == "sales-order.created"
    assert event.subject == "101"
    assert event.tenant_id == 1
    assert event.data.id == 1001
    assert event.data.total == "37.99"


@pytest.mark.asyncio
async def test_fetch_order_details():
    """Test fetching order via WooCommerceClient."""
    mock_transport = httpx.MockTransport(
        lambda req: httpx.Response(200, json=SAMPLE_ORDER_RAW)
    )
    async with httpx.AsyncClient(transport=mock_transport) as http_client:
        client = WooCommerceClient(
            "https://store.example.com",
            "ck_test",
            "cs_test",
            client=http_client,
        )
        order = await fetch_order_details(client, 1001)
        assert order.id == 1001
        assert order.total == "37.99"


@pytest.mark.asyncio
async def test_submit_order():
    """Test submitting order via WooCommerceClient."""
    mock_transport = httpx.MockTransport(
        lambda req: httpx.Response(201, json=SAMPLE_ORDER_RAW)
    )
    async with httpx.AsyncClient(transport=mock_transport) as http_client:
        client = WooCommerceClient(
            "https://store.example.com",
            "ck_test",
            "cs_test",
            client=http_client,
        )
        order = Order(status="processing", total="37.99")
        result = await submit_order(client, order)
        assert result["id"] == 1001
