"""Unit tests for Proquint syllable utilities."""

import pytest
from woocommerce_event.utils.proquint import (
    encode_numeric_ids_to_proquint,
    get_proquint_windmill_resource_path,
    proquint_to_uint16,
    uint16_to_proquint,
)


def test_uint16_to_proquint_and_back():
    """Test round-trip encoding and decoding of 16-bit integers."""
    values = [0, 1, 42, 101, 1000, 65535]
    for val in values:
        syllable = uint16_to_proquint(val)
        assert len(syllable) == 5
        decoded = proquint_to_uint16(syllable)
        assert decoded == val


def test_proquint_invalid_length():
    """Test error handling when decoding malformed syllable."""
    with pytest.raises(ValueError, match="must be exactly 5 characters"):
        proquint_to_uint16("abc")


def test_encode_numeric_ids_to_proquint_deterministic():
    """Test deterministic mapping of numeric tenant_id and site_id."""
    slug1 = encode_numeric_ids_to_proquint(42, 101)
    slug2 = encode_numeric_ids_to_proquint("42", "101")
    assert slug1 == slug2
    assert "_" in slug1
    parts = slug1.split("_")
    assert len(parts) == 2
    assert len(parts[0]) == 5
    assert len(parts[1]) == 5


def test_encode_numeric_ids_large_and_strings():
    """Test mapping for large numbers and string fallbacks."""
    slug_large = encode_numeric_ids_to_proquint(100000, 200000)
    assert len(slug_large.split("_")) == 2

    slug_str = encode_numeric_ids_to_proquint("acme_tenant", "main_store")
    assert len(slug_str.split("_")) == 2


def test_get_proquint_windmill_resource_path():
    """Test resource path generation."""
    path = get_proquint_windmill_resource_path(42, 101)
    slug = encode_numeric_ids_to_proquint(42, 101)
    assert path == f"f/woocommerce_event/{slug}_woocommerce"
