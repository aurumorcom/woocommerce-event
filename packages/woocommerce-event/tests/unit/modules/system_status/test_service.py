"""Unit tests for system status service functions."""

import httpx
import pytest
from fixtures.woocommerce_api_samples import SAMPLE_SYSTEM_STATUS_RAW
from woocommerce_event.integrations.woocommerce import WooCommerceClient
from woocommerce_event.modules.system_status.service import fetch_system_health


@pytest.mark.asyncio
async def test_fetch_system_health():
    """Test fetching system status via WooCommerceClient."""
    mock_transport = httpx.MockTransport(
        lambda req: httpx.Response(200, json=SAMPLE_SYSTEM_STATUS_RAW)
    )
    async with httpx.AsyncClient(transport=mock_transport) as http_client:
        client = WooCommerceClient(
            "https://store.example.com",
            "ck_test",
            "cs_test",
            client=http_client,
        )
        status = await fetch_system_health(client)
        assert status.environment is not None
        assert status.environment.version == "8.5.0"
        assert status.environment.wp_version == "6.4.2"
        assert status.database is not None
        assert status.database.wc_database_version == "8.5.0"
