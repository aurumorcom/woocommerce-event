"""External integration tests for order service against live/recorded endpoint."""

import pytest
from woocommerce_event.integrations.woocommerce import WooCommerceClient
from woocommerce_event.modules.orders.service import fetch_order_details
from woocommerce_event.schemas import Credentials
from tests.integration.external.conftest import execute_vcr_external_test


@pytest.mark.asyncio
async def test_external_fetch_order(
    live_credentials: Credentials, vcr_config: dict, vcr_cassette_dir
):
    """Test fetching order from live/recorded endpoint using VCR cassette."""
    cassette_path = vcr_cassette_dir / "test_external_fetch_order.yaml"

    async def run_test():
        async with WooCommerceClient(
            site_url=live_credentials.site_url,
            consumer_key=live_credentials.consumer_key,
            consumer_secret=live_credentials.consumer_secret,
        ) as client:
            orders = await client.list_orders(params={"per_page": 1})
            if orders and isinstance(orders, list) and len(orders) > 0:
                order_id = orders[0]["id"]
                order = await fetch_order_details(client, order_id)
                assert order.id == order_id
            else:
                assert isinstance(orders, list)

    await execute_vcr_external_test(cassette_path, vcr_config, run_test)
