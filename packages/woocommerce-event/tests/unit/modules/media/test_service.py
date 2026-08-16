"""Unit tests for media service functions."""

import httpx
import pytest
from fixtures.woocommerce_api_samples import SAMPLE_MEDIA_RAW
from woocommerce_event.integrations.woocommerce import WooCommerceClient
from woocommerce_event.modules.media.service import (
    parse_media_webhook,
    upload_media,
)


def test_parse_media_webhook():
    """Test parsing media webhook into CloudEvent."""
    event = parse_media_webhook(
        raw_json=SAMPLE_MEDIA_RAW,
        tenant_id=1,
        site_id=101,
        action="created",
    )
    assert event.type == "media.created"
    assert event.subject == "101"
    assert event.tenant_id == 1
    assert event.data.id == 101
    assert event.data.mime_type == "image/jpeg"


@pytest.mark.asyncio
async def test_upload_media():
    """Test uploading media via WooCommerceClient."""
    mock_transport = httpx.MockTransport(
        lambda req: httpx.Response(201, json=SAMPLE_MEDIA_RAW)
    )
    async with httpx.AsyncClient(transport=mock_transport) as http_client:
        client = WooCommerceClient(
            "https://store.example.com",
            "ck_test",
            "cs_test",
            client=http_client,
        )
        media_item = await upload_media(
            client=client,
            filename="shirt.jpg",
            content_type="image/jpeg",
            data=b"fake_image_bytes",
        )
        assert media_item.id == 101
        assert (
            media_item.source_url
            == "https://store.example.com/wp-content/uploads/shirt.jpg"
        )
