"""External integration tests for WooCommerce API client against live/recorded endpoints."""

import pytest
from woocommerce_event.integrations.woocommerce import WooCommerceClient
from woocommerce_event.schemas import Credentials
from tests.integration.external.conftest import execute_vcr_external_test


@pytest.mark.asyncio
async def test_live_woocommerce_api_connectivity(
    live_credentials: Credentials, vcr_config: dict, vcr_cassette_dir
):
    """Test live connectivity and endpoint resolution against target WooCommerce site using VCR cassette."""
    cassette_path = vcr_cassette_dir / "test_live_woocommerce_api_connectivity.yaml"

    async def run_test():
        async with WooCommerceClient(
            site_url=live_credentials.site_url,
            consumer_key=live_credentials.consumer_key,
            consumer_secret=live_credentials.consumer_secret,
        ) as client:
            status = await client.get_system_status()
            assert isinstance(status, dict)

    await execute_vcr_external_test(cassette_path, vcr_config, run_test)
