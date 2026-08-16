"""External integration test for live webhook provisioning against WooCommerce store."""

import pytest
from woocommerce_event.integrations.woocommerce import WooCommerceClient
from woocommerce_event.modules.webhooks.service import provision_webhooks
from woocommerce_event.schemas import Credentials
from tests.integration.external.conftest import execute_vcr_external_test


@pytest.mark.asyncio
async def test_external_provision_webhooks(
    live_credentials: Credentials, vcr_config: dict, vcr_cassette_dir
):
    """Test provisioning live webhooks in WooCommerce store using VCR cassette."""
    cassette_path = vcr_cassette_dir / "test_external_provision_webhooks.yaml"

    async def run_test():
        async with WooCommerceClient(
            site_url=live_credentials.site_url,
            consumer_key=live_credentials.consumer_key,
            consumer_secret=live_credentials.consumer_secret,
        ) as client:
            results = await provision_webhooks(
                client=client,
                delivery_url="https://ingress.aurumor.com/webhooks/woocommerce",
                secret="whsec_live_12345",
                topics=["order.created", "order.updated"],
            )
            assert isinstance(results, list)
            assert len(results) >= 2
            for item in results:
                assert "id" in item
                assert item.get("status") == "active"

    await execute_vcr_external_test(cassette_path, vcr_config, run_test)
