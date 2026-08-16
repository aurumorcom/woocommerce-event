"""Unit tests for WooCommerceEventClient facade."""

from datetime import UTC, datetime

import pytest
from woocommerce_event.client import WooCommerceEventClient
from woocommerce_event.modules.products.schemas import Product, ProductCreated
from woocommerce_event.repositories.memory import (
    MemoryCredentialsRepository,
    MemoryStateRepository,
)
from woocommerce_event.schemas import Credentials


@pytest.mark.asyncio
async def test_client_lifecycle():
    """Test WooCommerceEventClient async context manager enter and exit."""
    async with WooCommerceEventClient() as client:
        assert client is not None
        assert client.event_client is not None


@pytest.mark.asyncio
async def test_client_publish_event(captured_logs):
    """Test publishing event via WooCommerceEventClient with canonical topic."""
    client = WooCommerceEventClient()
    product = Product(
        id=1,
        name="Test Item",
        sku="TEST-SKU",
    )
    event = ProductCreated(
        id="evt-1",
        source="woocommerce://101/products",
        subject="101",
        tenant_id=1,
        time=datetime.now(UTC),
        data=product,
    )

    resp = await client.publish_event(topic="product", event=event)
    assert resp.topic == "product"


@pytest.mark.asyncio
async def test_client_publish_event_invalid_topic_rejected():
    """Test publishing event with non-canonical topic raises ValueError."""
    client = WooCommerceEventClient()
    product = Product(
        id=1,
        name="Test Item",
        sku="TEST-SKU",
    )
    event = ProductCreated(
        id="evt-1",
        source="woocommerce://101/products",
        subject="101",
        tenant_id=1,
        time=datetime.now(UTC),
        data=product,
    )

    with pytest.raises(ValueError, match="Invalid topic 'woocommerce.products.events'"):
        await client.publish_event(topic="woocommerce.products.events", event=event)


@pytest.mark.asyncio
async def test_client_get_authenticated_wc_client_cache_hit_and_miss(
    sample_credentials: Credentials,
):
    """Test credentials resolution, caching, and cache hit flow."""
    creds_repo = MemoryCredentialsRepository()
    creds_repo.add_credentials(1, 101, sample_credentials)
    state_repo = MemoryStateRepository()

    client = WooCommerceEventClient(credentials_repo=creds_repo, state_repo=state_repo)

    # 1. First call - Cache Miss
    wc_client_1 = await client.get_authenticated_wc_client(1, 101)
    assert wc_client_1.site_url == "https://store.example.com"
    assert wc_client_1.consumer_key == sample_credentials.consumer_key

    # 2. Second call - Cache Hit
    wc_client_2 = await client.get_authenticated_wc_client(1, 101)
    assert wc_client_2.site_url == "https://store.example.com"

    await client.aclose()
