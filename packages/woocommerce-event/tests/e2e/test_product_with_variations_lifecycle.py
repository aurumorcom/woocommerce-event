"""E2E Test: Full lifecycle of a parent product with variation generation."""

import httpx
import pytest
from fixtures.woocommerce_api_samples import (
    SAMPLE_PRODUCT_RAW,
    SAMPLE_VARIATION_RAW,
)
from woocommerce_event.client import WooCommerceEventClient
from woocommerce_event.modules.products.schemas import (
    Product,
    ProductAttribute,
)
from woocommerce_event.modules.products.service import submit_product
from woocommerce_event.modules.variations.schemas import (
    Variation,
    VariationAttribute,
)
from woocommerce_event.modules.variations.service import submit_variation
from woocommerce_event.repositories.memory import MemoryCredentialsRepository
from woocommerce_event.schemas import Credentials


@pytest.mark.asyncio
async def test_product_with_variations_lifecycle_flow(
    sample_credentials: Credentials,
):
    """Test full journey: create variable product -> attach attributes -> create variations."""
    creds_repo = MemoryCredentialsRepository()
    creds_repo.add_credentials(1, 101, sample_credentials)

    def handler(request: httpx.Request) -> httpx.Response:
        if "variations" in str(request.url):
            return httpx.Response(201, json=SAMPLE_VARIATION_RAW)
        return httpx.Response(201, json=SAMPLE_PRODUCT_RAW)

    mock_transport = httpx.MockTransport(handler)
    async with (
        httpx.AsyncClient(transport=mock_transport) as http_client,
        WooCommerceEventClient(credentials_repo=creds_repo) as client,
    ):
        wc_client = await client.get_authenticated_wc_client(1, 101)
        wc_client.client = http_client

        # 1. Create parent variable product
        parent_product = Product(
            name="Premium Hoodie",
            type="variable",
            sku="HOODIE-VAR",
            attributes=[
                ProductAttribute(name="Size", variation=True, options=["M", "L"])
            ],
        )
        created_parent = await submit_product(client=wc_client, product=parent_product)
        assert created_parent["id"] == 799

        # 2. Add variation
        variation = Variation(
            sku="HOODIE-VAR-M",
            regular_price="49.99",
            attributes=[VariationAttribute(name="Size", option="M")],
        )
        created_var = await submit_variation(
            client=wc_client,
            product_id=created_parent["id"],
            variation=variation,
        )
        assert created_var["id"] == 801
        assert created_var["sku"] == "TSHIRT-PREM-M"
