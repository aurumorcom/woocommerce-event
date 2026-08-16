"""Unit tests for analyze_woocommerce_fields script."""

from scripts.analyze_woocommerce_fields import (
    classify_fields,
    extract_properties_from_schema,
)


def test_classify_fields():
    """Test classification of core vs computed properties."""
    sample_props = {
        "id": {"type": "integer", "readonly": True, "description": "Unique identifier"},
        "name": {"type": "string", "required": True, "description": "Item name"},
        "status": {
            "type": "string",
            "enum": ["publish", "draft"],
            "default": "publish",
        },
    }

    result = classify_fields(sample_props)
    assert "name" in result["core_fields"]
    assert "status" in result["core_fields"]
    assert "id" in result["computed_fields"]
    assert result["enums"]["status"] == ["publish", "draft"]
    assert result["total_properties"] == 3


def test_extract_properties_from_schema():
    """Test extracting properties from nested schema."""
    schema_wrapper = {
        "schema": {
            "properties": {
                "sku": {"type": "string"},
            }
        }
    }
    props = extract_properties_from_schema(schema_wrapper)
    assert "sku" in props
