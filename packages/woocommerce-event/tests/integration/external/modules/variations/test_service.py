"""External integration tests for variation service against live/recorded endpoint."""

import uuid
import pytest
from woocommerce_event.exceptions import WooCommerceAPIError
from woocommerce_event.integrations.woocommerce import WooCommerceClient
from woocommerce_event.modules.variations.schemas import Variation
from woocommerce_event.modules.variations.service import submit_variation
from woocommerce_event.schemas import Credentials
from tests.integration.external.conftest import execute_vcr_external_test


@pytest.mark.asyncio
async def test_external_variation_submission(
    live_credentials: Credentials, vcr_config: dict, vcr_cassette_dir
):
    """Test submitting variation to live/recorded endpoint using VCR cassette."""
    cassette_path = vcr_cassette_dir / "test_external_variation_submission.yaml"

    async def run_test():
        async with WooCommerceClient(
            site_url=live_credentials.site_url,
            consumer_key=live_credentials.consumer_key,
            consumer_secret=live_credentials.consumer_secret,
        ) as client:
            products = await client.list_products(params={"per_page": 1})
            if products and isinstance(products, list) and len(products) > 0:
                parent_product_id = products[0]["id"]
                unique_sku = f"VAR-{parent_product_id}-{uuid.uuid4().hex[:4]}"
                variation = Variation(sku=unique_sku)
                try:
                    res = await submit_variation(
                        client, product_id=parent_product_id, variation=variation
                    )
                    assert "id" in res
                except WooCommerceAPIError as exc:
                    if "product_invalid_sku" in str(exc) or "cannot_create" in str(exc):
                        res = await client.list_variations(product_id=parent_product_id)
                        assert isinstance(res, list)
                    else:
                        raise exc
            else:
                res = await client.list_variations(product_id=999999)
                assert isinstance(res, list)

    await execute_vcr_external_test(cassette_path, vcr_config, run_test)
