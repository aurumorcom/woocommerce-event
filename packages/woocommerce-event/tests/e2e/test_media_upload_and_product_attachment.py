"""E2E Test: Media binary upload and linking image to WooCommerce product."""

import httpx
import pytest
from fixtures.woocommerce_api_samples import (
    SAMPLE_MEDIA_RAW,
    SAMPLE_PRODUCT_RAW,
)
from woocommerce_event.client import WooCommerceEventClient
from woocommerce_event.modules.media.service import upload_media
from woocommerce_event.modules.products.schemas import (
    Product,
    ProductImage,
)
from woocommerce_event.modules.products.service import submit_product
from woocommerce_event.repositories.memory import MemoryCredentialsRepository
from woocommerce_event.schemas import Credentials


@pytest.mark.asyncio
async def test_media_upload_and_product_attachment_flow(
    sample_credentials: Credentials,
):
    """Test full journey: upload media binary -> receive media ID -> attach to product."""
    creds_repo = MemoryCredentialsRepository()
    creds_repo.add_credentials(1, 101, sample_credentials)

    def handler(request: httpx.Request) -> httpx.Response:
        if "wp/v2/media" in str(request.url):
            return httpx.Response(201, json=SAMPLE_MEDIA_RAW)
        return httpx.Response(201, json=SAMPLE_PRODUCT_RAW)

    mock_transport = httpx.MockTransport(handler)
    async with (
        httpx.AsyncClient(transport=mock_transport) as http_client,
        WooCommerceEventClient(credentials_repo=creds_repo) as client,
    ):
        wc_client = await client.get_authenticated_wc_client(1, 101)
        wc_client.client = http_client

        # 1. Upload media
        media_item = await upload_media(
            client=wc_client,
            filename="shirt.jpg",
            content_type="image/jpeg",
            data=b"fake_image_bytes",
        )
        assert media_item.id == 101

        # 2. Attach uploaded image to product
        product = Product(
            name="T-Shirt With Image",
            sku="TSHIRT-IMG",
            images=[ProductImage(id=media_item.id, src=media_item.source_url or "")],
        )
        created_prod = await submit_product(client=wc_client, product=product)
        assert created_prod["id"] == 799
