"""E2E Test: Site Provisioning -> Topology Registration -> Webhook Subscription."""

import httpx
import pytest
from fixtures.woocommerce_api_samples import SAMPLE_WEBHOOK_RAW
from woocommerce_event.client import WooCommerceEventClient
from woocommerce_event.modules.sites.service import register_site_topology
from woocommerce_event.modules.webhooks.service import provision_webhooks
from woocommerce_event.repositories.memory import MemoryCredentialsRepository
from woocommerce_event.schemas import Credentials, Site


@pytest.mark.asyncio
async def test_site_provisioning_and_webhook_subscription_flow(
    sample_credentials: Credentials,
):
    """Test full journey: configure tenant site -> register topology -> provision default inbound webhooks in WooCommerce."""
    creds_repo = MemoryCredentialsRepository()
    creds_repo.add_credentials(1, 101, sample_credentials)

    mock_transport = httpx.MockTransport(
        lambda req: httpx.Response(201, json=SAMPLE_WEBHOOK_RAW)
    )
    async with (
        httpx.AsyncClient(transport=mock_transport) as http_client,
        WooCommerceEventClient(credentials_repo=creds_repo) as client,
    ):
        wc_client = await client.get_authenticated_wc_client(1, 101)
        wc_client.client = http_client

        # 1. Register streaming topology
        site_context = Site(tenant_id=1, site_id=101, environment="production")
        await register_site_topology(client=client, site_context=site_context)

        # 2. Provision default 2 order webhooks on WooCommerce store (order.created, order.updated)
        webhooks = await provision_webhooks(
            client=wc_client,
            delivery_url="https://ingress.enterprise.com/wc",
            secret="whsec_e2e_secret",
        )
        assert len(webhooks) == 2
