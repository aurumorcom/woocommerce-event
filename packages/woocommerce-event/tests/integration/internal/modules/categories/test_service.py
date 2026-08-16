"""Internal integration test for category webhook to Kafka pipeline."""

import pytest
from fixtures.woocommerce_api_samples import SAMPLE_CATEGORY_RAW
from woocommerce_event.client import WooCommerceEventClient
from woocommerce_event.modules.categories.service import (
    parse_category_webhook,
)


@pytest.mark.asyncio
async def test_category_webhook_to_event_pipeline():
    """Test category webhook parsing and publishing pipeline."""
    async with WooCommerceEventClient() as client:
        event = parse_category_webhook(SAMPLE_CATEGORY_RAW, tenant_id=1, site_id=101)
        resp = await client.publish_event(topic="item-category", event=event)
        assert resp.topic == "item-category"
        assert resp.partition_key == "1"
