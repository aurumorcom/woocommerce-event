"""Unit tests for generate_woocommerce_pydantic script."""

from scripts.generate_woocommerce_pydantic import (
    generate_pydantic_code_for_schema,
    pythonize_name,
)


def test_pythonize_name():
    """Test converting property names to safe Python identifiers."""
    assert pythonize_name("regular_price") == "regular_price"
    assert pythonize_name("class") == "class_val"
    assert pythonize_name("from") == "from_val"
    assert pythonize_name("menu-order") == "menu_order"


def test_generate_pydantic_code_for_schema():
    """Test generating Pydantic class code."""
    props = {
        "id": {"type": "integer", "readonly": True, "description": "ID"},
        "name": {"type": "string", "required": True, "description": "Name"},
        "price": {"type": "string", "default": "0.00", "description": "Price"},
    }
    code = generate_pydantic_code_for_schema("SampleProduct", props)
    assert "class SampleProduct(BaseModel):" in code
    assert "name: str = Field" in code
    assert "price: str = Field" in code
    assert "id_val: int | None = Field" in code
