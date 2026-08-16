"""Unit tests for attribute schemas."""

from fixtures.woocommerce_api_samples import (
    SAMPLE_ATTRIBUTE_RAW,
    SAMPLE_ATTRIBUTE_TERM_RAW,
)
from woocommerce_event.modules.attributes.schemas import (
    Attribute,
    AttributeCreated,
    AttributeTerm,
    AttributeTermCreated,
)


def test_attribute_model_validation():
    """Test validating sample attribute payload."""
    attr = Attribute.model_validate(SAMPLE_ATTRIBUTE_RAW)
    assert attr.id == 1
    assert attr.name == "Size"
    assert attr.type == "select"


def test_attribute_term_model_validation():
    """Test validating sample attribute term payload."""
    term = AttributeTerm.model_validate(SAMPLE_ATTRIBUTE_TERM_RAW)
    assert term.id == 31
    assert term.name == "Medium"
    assert term.slug == "m"


def test_attribute_cloudevents():
    """Test AttributeCreated and AttributeTermCreated CloudEvent schemas."""
    attr = Attribute.model_validate(SAMPLE_ATTRIBUTE_RAW)
    event_attr = AttributeCreated(
        id="evt-attr-1",
        source="woocommerce://101/attributes",
        subject="101",
        tenant_id=1,
        data=attr,
    )
    assert event_attr.type == "item-attribute.created"
    assert event_attr.subject == "101"
    assert event_attr.tenant_id == 1

    term = AttributeTerm.model_validate(SAMPLE_ATTRIBUTE_TERM_RAW)
    event_term = AttributeTermCreated(
        id="evt-term-1",
        source="woocommerce://101/attributes/terms",
        subject="101",
        tenant_id=1,
        data=term,
    )
    assert event_term.type == "item-attribute-value.created"
    assert event_term.subject == "101"
    assert event_term.tenant_id == 1
