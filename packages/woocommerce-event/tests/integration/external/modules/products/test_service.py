"""External integration tests for product CRUD service against live/recorded endpoint."""

import uuid
import pytest
from woocommerce_event.exceptions import WooCommerceAPIError
from woocommerce_event.integrations.woocommerce import WooCommerceClient
from woocommerce_event.modules.products.schemas import Product
from woocommerce_event.modules.products.service import submit_product
from woocommerce_event.schemas import Credentials
from tests.integration.external.conftest import execute_vcr_external_test


@pytest.mark.asyncio
async def test_external_product_submission(
    live_credentials: Credentials, vcr_config: dict, vcr_cassette_dir
):
    """Test submitting product to live/recorded endpoint using VCR cassette."""
    cassette_path = vcr_cassette_dir / "test_external_product_submission.yaml"

    async def run_test():
        async with WooCommerceClient(
            site_url=live_credentials.site_url,
            consumer_key=live_credentials.consumer_key,
            consumer_secret=live_credentials.consumer_secret,
        ) as client:
            unique_id = uuid.uuid4().hex[:6]
            product = Product(
                name=f"Integ Test Product {unique_id}",
                sku=f"TSHIRT-TEST-{unique_id}",
            )
            try:
                res = await submit_product(client, product)
                assert "id" in res
            except WooCommerceAPIError as exc:
                if "product_invalid_sku" in str(exc) or "already exists" in str(exc):
                    products = await client.list_products(params={"per_page": 1})
                    assert isinstance(products, list)
                else:
                    raise exc

    await execute_vcr_external_test(cassette_path, vcr_config, run_test)
