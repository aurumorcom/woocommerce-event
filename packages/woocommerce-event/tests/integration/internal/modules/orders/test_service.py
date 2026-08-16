"""Internal integration test for order webhook to Kafka pipeline."""

import pytest
from fixtures.woocommerce_api_samples import SAMPLE_ORDER_RAW
from woocommerce_event.client import WooCommerceEventClient
from woocommerce_event.modules.orders.service import parse_order_webhook


@pytest.mark.asyncio
async def test_order_webhook_to_event_pipeline():
    """Test order webhook parsing and publishing pipeline."""
    async with WooCommerceEventClient() as client:
        event = parse_order_webhook(SAMPLE_ORDER_RAW, tenant_id=1, site_id=101)
        resp = await client.publish_event(topic="sales-order", event=event)
        assert resp.topic == "sales-order"
        assert resp.partition_key == "1"
