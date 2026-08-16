"""Unit tests for media schemas."""

from fixtures.woocommerce_api_samples import SAMPLE_MEDIA_RAW
from woocommerce_event.modules.media.schemas import MediaCreated, MediaItem


def test_media_model_validation():
    """Test validating sample WordPress media item."""
    media = MediaItem.model_validate(SAMPLE_MEDIA_RAW)
    assert media.id == 101
    assert media.mime_type == "image/jpeg"
    assert media.media_details is not None
    assert media.media_details.width == 1200


def test_media_created_cloudevent():
    """Test MediaCreated CloudEvent schema."""
    media = MediaItem.model_validate(SAMPLE_MEDIA_RAW)
    event = MediaCreated(
        id="evt-media-1",
        source="woocommerce://101/media",
        subject="101",
        tenant_id=1,
        data=media,
    )
    assert event.type == "media.created"
    assert event.subject == "101"
    assert event.tenant_id == 1
    assert event.data.id == 101
