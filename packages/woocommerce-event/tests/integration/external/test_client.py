"""External integration tests for client against live/recorded WooCommerce endpoints."""

import pytest
from woocommerce_event.client import WooCommerceEventClient
from woocommerce_event.repositories.memory import MemoryCredentialsRepository
from woocommerce_event.schemas import Credentials
from tests.integration.external.conftest import execute_vcr_external_test


@pytest.mark.asyncio
async def test_external_client_live_resolution(
    live_credentials: Credentials, vcr_config: dict, vcr_cassette_dir
):
    """Test authenticated facade client resolution with live site credentials using VCR cassette."""
    creds_repo = MemoryCredentialsRepository()
    creds_repo.add_credentials(1, "live_site", live_credentials)
    cassette_path = vcr_cassette_dir / "test_external_client_live_resolution.yaml"

    async def run_test():
        async with WooCommerceEventClient(credentials_repo=creds_repo) as client:
            wc_client = await client.get_authenticated_wc_client(1, "live_site")
            assert wc_client.site_url == live_credentials.site_url.rstrip("/")
            status = await wc_client.get_system_status()
            assert isinstance(status, dict)

    await execute_vcr_external_test(cassette_path, vcr_config, run_test)
