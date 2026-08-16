"""Internal integration test for client facade with fake repos and mock event client."""

from datetime import UTC, datetime

import pytest
from python_event.client import EventClient
from woocommerce_event.client import WooCommerceEventClient
from woocommerce_event.modules.products.schemas import Product, ProductCreated
from woocommerce_event.repositories.memory import (
    MemoryCredentialsRepository,
    MemoryStateRepository,
)
from woocommerce_event.schemas import Credentials


@pytest.mark.asyncio
async def test_internal_client_pipeline(sample_credentials: Credentials, captured_logs):
    """Test full client pipeline: credential retrieval -> caching -> event dispatch."""
    creds_repo = MemoryCredentialsRepository()
    creds_repo.add_credentials(1, 101, sample_credentials)
    state_repo = MemoryStateRepository()
    event_client = EventClient()

    async with WooCommerceEventClient(
        event_client=event_client,
        credentials_repo=creds_repo,
        state_repo=state_repo,
    ) as client:
        # Resolve client
        wc_client = await client.get_authenticated_wc_client(1, 101)
        assert wc_client.site_url == "https://store.example.com"

        # Dispatch event
        prod = Product(
            id=99,
            name="Integrated Product",
            sku="INT-99",
        )
        event = ProductCreated(
            id="evt-int-1",
            source="woocommerce://101/products",
            subject="101",
            tenant_id=1,
            time=datetime.now(UTC),
            data=prod,
        )

        resp = await client.publish_event(topic="product", event=event)
        assert resp.topic == "product"
        assert resp.partition_key == "1"
