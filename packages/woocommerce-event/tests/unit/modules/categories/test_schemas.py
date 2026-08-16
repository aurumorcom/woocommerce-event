"""Unit tests for category schemas."""

from fixtures.woocommerce_api_samples import SAMPLE_CATEGORY_RAW
from woocommerce_event.modules.categories.schemas import (
    Category,
    CategoryCreated,
)


def test_category_model_validation():
    """Test validating sample category payload."""
    cat = Category.model_validate(SAMPLE_CATEGORY_RAW)
    assert cat.id == 15
    assert cat.name == "Clothing"
    assert cat.count == 24


def test_category_created_cloudevent():
    """Test CategoryCreated CloudEvent schema."""
    cat = Category.model_validate(SAMPLE_CATEGORY_RAW)
    event = CategoryCreated(
        id="evt-cat-1",
        source="woocommerce://101/categories",
        subject="101",
        tenant_id=1,
        data=cat,
    )
    assert event.type == "item-category.created"
    assert event.subject == "101"
    assert event.tenant_id == 1
    assert event.data.id == 15
