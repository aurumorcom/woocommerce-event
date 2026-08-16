"""Unit tests for variation schemas."""

from fixtures.woocommerce_api_samples import SAMPLE_VARIATION_RAW
from woocommerce_event.modules.variations.schemas import (
    Variation,
    VariationCreated,
)


def test_variation_model_validation():
    """Test validating sample variation payload."""
    variation = Variation.model_validate(SAMPLE_VARIATION_RAW)
    assert variation.id == 801
    assert variation.parent_id == 799
    assert variation.sku == "TSHIRT-PREM-M"
    assert len(variation.attributes) == 1
    assert variation.attributes[0].option == "M"


def test_variation_created_cloudevent():
    """Test VariationCreated CloudEvent schema."""
    variation = Variation.model_validate(SAMPLE_VARIATION_RAW)
    event = VariationCreated(
        id="evt-var-1",
        source="woocommerce://101/products/799/variations",
        subject="101",
        tenant_id=1,
        data=variation,
    )
    assert event.type == "product-variant.created"
    assert event.subject == "101"
    assert event.tenant_id == 1
    assert event.data.id == 801
