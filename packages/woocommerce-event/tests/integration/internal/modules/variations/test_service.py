"""Internal integration test for variation webhook to Kafka pipeline."""

import pytest
from fixtures.woocommerce_api_samples import SAMPLE_VARIATION_RAW
from woocommerce_event.client import WooCommerceEventClient
from woocommerce_event.modules.variations.service import (
    parse_variation_webhook,
)


@pytest.mark.asyncio
async def test_variation_webhook_to_event_pipeline():
    """Test variation webhook parsing and publishing pipeline."""
    async with WooCommerceEventClient() as client:
        event = parse_variation_webhook(
            SAMPLE_VARIATION_RAW,
            parent_id=799,
            tenant_id=1,
            site_id=101,
        )
        resp = await client.publish_event(topic="product-variant", event=event)
        assert resp.topic == "product-variant"
        assert resp.partition_key == "1"
