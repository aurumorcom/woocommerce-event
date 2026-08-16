"""Internal integration test for product webhook to Kafka pipeline."""

import pytest
from fixtures.woocommerce_api_samples import SAMPLE_PRODUCT_RAW
from woocommerce_event.client import WooCommerceEventClient
from woocommerce_event.modules.products.service import parse_product_webhook


@pytest.mark.asyncio
async def test_product_webhook_to_event_pipeline():
    """Test product webhook parsing and publishing pipeline."""
    async with WooCommerceEventClient() as client:
        event = parse_product_webhook(SAMPLE_PRODUCT_RAW, tenant_id=1, site_id=101)
        resp = await client.publish_event(topic="product", event=event)
        assert resp.topic == "product"
        assert resp.partition_key == "1"
