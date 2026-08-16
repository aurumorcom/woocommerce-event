"""Unit tests for WooCommerceClient."""

import httpx
import pytest
from fixtures.woocommerce_api_samples import (
    SAMPLE_ATTRIBUTE_RAW,
    SAMPLE_CATEGORY_RAW,
    SAMPLE_ORDER_RAW,
    SAMPLE_PRODUCT_RAW,
    SAMPLE_SYSTEM_STATUS_RAW,
    SAMPLE_TAG_RAW,
    SAMPLE_VARIATION_RAW,
    SAMPLE_WEBHOOK_RAW,
)
from woocommerce_event.exceptions import (
    WooCommerceAuthenticationError,
)
from woocommerce_event.integrations.woocommerce import WooCommerceClient


@pytest.mark.asyncio
async def test_woocommerce_api_client_request_success():
    """Test standard successful REST API request."""
    mock_transport = httpx.MockTransport(
        lambda req: httpx.Response(200, json=SAMPLE_PRODUCT_RAW)
    )
    async with httpx.AsyncClient(transport=mock_transport) as http_client:
        client = WooCommerceClient(
            "https://store.example.com", "ck_test", "cs_test", client=http_client
        )
        product = await client.get_product(799)
        assert product["id"] == 799
        assert product["name"] == "Premium T-Shirt"


@pytest.mark.asyncio
async def test_woocommerce_api_client_authentication_error():
    """Test 401 response raises WooCommerceAuthenticationError."""
    mock_transport = httpx.MockTransport(
        lambda req: httpx.Response(401, text="Unauthorized consumer key")
    )
    async with httpx.AsyncClient(transport=mock_transport) as http_client:
        client = WooCommerceClient(
            "https://store.example.com", "ck_bad", "cs_bad", client=http_client
        )
        with pytest.raises(WooCommerceAuthenticationError):
            await client.get_product(799)


@pytest.mark.asyncio
async def test_woocommerce_api_client_endpoints():
    """Test multiple 1:1 API endpoint methods."""

    def handler(request: httpx.Request) -> httpx.Response:
        url_str = str(request.url)
        if "wc/v3/products/799/variations" in url_str:
            return httpx.Response(200, json=[SAMPLE_VARIATION_RAW])
        if "wc/v3/orders/1001" in url_str:
            return httpx.Response(200, json=SAMPLE_ORDER_RAW)
        if "wc/v3/products/categories" in url_str:
            return httpx.Response(200, json=[SAMPLE_CATEGORY_RAW])
        if "wc/v3/products/tags" in url_str:
            return httpx.Response(200, json=[SAMPLE_TAG_RAW])
        if "wc/v3/products/attributes" in url_str:
            return httpx.Response(200, json=[SAMPLE_ATTRIBUTE_RAW])
        if "wc/v3/webhooks" in url_str:
            return httpx.Response(200, json=[SAMPLE_WEBHOOK_RAW])
        if "wc/v3/system_status" in url_str:
            return httpx.Response(200, json=SAMPLE_SYSTEM_STATUS_RAW)
        return httpx.Response(200, json=SAMPLE_PRODUCT_RAW)

    mock_transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=mock_transport) as http_client:
        client = WooCommerceClient(
            "https://store.example.com", "ck_test", "cs_test", client=http_client
        )
        assert len(await client.list_variations(799)) == 1
        assert (await client.get_order(1001))["id"] == 1001
        assert len(await client.list_categories()) == 1
        assert len(await client.list_tags()) == 1
        assert len(await client.list_attributes()) == 1
        assert len(await client.list_webhooks()) == 1
        assert (await client.get_system_status())["environment"]["version"] == "8.5.0"
