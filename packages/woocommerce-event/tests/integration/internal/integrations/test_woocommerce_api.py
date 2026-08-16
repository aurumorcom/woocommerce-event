"""Internal integration tests for WooCommerceClient with mock HTTP server."""

import httpx
import pytest
from fixtures.woocommerce_api_samples import SAMPLE_PRODUCT_RAW
from woocommerce_event.integrations.woocommerce import WooCommerceClient


@pytest.mark.asyncio
async def test_woocommerce_api_client_batch_products():
    """Test batch product creation."""
    mock_batch_response = {
        "create": [SAMPLE_PRODUCT_RAW],
        "update": [],
        "delete": [],
    }
    mock_transport = httpx.MockTransport(
        lambda req: httpx.Response(200, json=mock_batch_response)
    )
    async with httpx.AsyncClient(transport=mock_transport) as http_client:
        client = WooCommerceClient(
            "https://store.example.com", "ck_test", "cs_test", client=http_client
        )
        resp = await client.batch_products(
            {"create": [{"name": "Batch Item", "sku": "B-1"}]}
        )
        assert len(resp["create"]) == 1
