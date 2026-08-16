"""Unit tests for tag schemas."""

from fixtures.woocommerce_api_samples import SAMPLE_TAG_RAW
from woocommerce_event.modules.tags.schemas import Tag, TagCreated


def test_tag_model_validation():
    """Test validating sample tag payload."""
    tag = Tag.model_validate(SAMPLE_TAG_RAW)
    assert tag.id == 22
    assert tag.name == "Summer"
    assert tag.count == 8


def test_tag_created_cloudevent():
    """Test TagCreated CloudEvent schema."""
    tag = Tag.model_validate(SAMPLE_TAG_RAW)
    event = TagCreated(
        id="evt-tag-1",
        source="woocommerce://101/tags",
        subject="101",
        tenant_id=1,
        data=tag,
    )
    assert event.type == "item-tag.created"
    assert event.subject == "101"
    assert event.tenant_id == 1
    assert event.data.id == 22
