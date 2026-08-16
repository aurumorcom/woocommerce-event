"""External integration tests for category service against live/recorded endpoint."""

import uuid
import pytest
from woocommerce_event.exceptions import WooCommerceAPIError
from woocommerce_event.integrations.woocommerce import WooCommerceClient
from woocommerce_event.modules.categories.schemas import Category
from woocommerce_event.modules.categories.service import submit_category
from woocommerce_event.schemas import Credentials
from tests.integration.external.conftest import execute_vcr_external_test


@pytest.mark.asyncio
async def test_external_category_submission(
    live_credentials: Credentials, vcr_config: dict, vcr_cassette_dir
):
    """Test category creation against live/recorded endpoint using VCR cassette."""
    cassette_path = vcr_cassette_dir / "test_external_category_submission.yaml"

    async def run_test():
        async with WooCommerceClient(
            site_url=live_credentials.site_url,
            consumer_key=live_credentials.consumer_key,
            consumer_secret=live_credentials.consumer_secret,
        ) as client:
            unique_name = f"Integ Category {uuid.uuid4().hex[:6]}"
            cat = Category(name=unique_name)
            try:
                res = await submit_category(client, cat)
                assert "id" in res
            except WooCommerceAPIError as exc:
                if "term_exists" in str(exc):
                    categories = await client.list_categories(params={"per_page": 1})
                    assert isinstance(categories, list)
                else:
                    raise exc

    await execute_vcr_external_test(cassette_path, vcr_config, run_test)
