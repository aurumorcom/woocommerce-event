"""Unit tests for product schemas."""

from fixtures.woocommerce_api_samples import SAMPLE_PRODUCT_RAW
from woocommerce_event.modules.products.schemas import (
    Product,
    ProductCreated,
)


def test_product_model_validation():
    """Test validating sample WooCommerce product."""
    product = Product.model_validate(SAMPLE_PRODUCT_RAW)
    assert product.id == 799
    assert product.name == "Premium T-Shirt"
    assert product.sku == "TSHIRT-PREM"
    assert len(product.attributes) == 1
    assert product.attributes[0].options == ["S", "M", "L"]


def test_product_created_cloudevent():
    """Test ProductCreated CloudEvent schema with pure entity payload."""
    product = Product.model_validate(SAMPLE_PRODUCT_RAW)
    event = ProductCreated(
        id="evt-101",
        source="woocommerce://101/products",
        subject="101",
        tenant_id=1,
        data=product,
    )
    assert event.type == "product.created"
    assert event.subject == "101"
    assert event.tenant_id == 1
    assert event.data.id == 799
    assert event.data.sku == "TSHIRT-PREM"
