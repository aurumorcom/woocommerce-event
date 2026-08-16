"""Unit tests for extract_woocommerce_schemas script."""

import httpx
import pytest

from scripts.extract_woocommerce_schemas import fetch_schema


@pytest.mark.asyncio
async def test_fetch_schema_success():
    """Test schema fetch via OPTIONS request."""
    mock_schema = {
        "namespace": "wc/v3",
        "endpoints": [],
        "schema": {"properties": {"id": {"type": "integer"}}},
    }
    mock_transport = httpx.MockTransport(
        lambda req: httpx.Response(200, json=mock_schema)
    )
    async with httpx.AsyncClient(transport=mock_transport) as client:
        data = await fetch_schema(client, "TEST_SCHEMA.json", "/wp-json/wc/v3/products")
        assert data is not None
        assert "namespace" in data
