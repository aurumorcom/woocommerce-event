import json
from pathlib import Path
from unittest.mock import AsyncMock, patch

import httpx
import pytest

from scripts.extract_wordpress_schemas import ENDPOINTS, fetch_schema


@pytest.mark.anyio
async def test_fetch_schema_success(tmp_path: Path):
    mock_response = AsyncMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "namespace": "wc/v3",
        "schema": {"type": "object"},
    }
    mock_response.content = b'{"namespace": "wc/v3"}'

    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.options.return_value = mock_response

    target_file = tmp_path / "TEST_SCHEMA.json"

    with patch("scripts.extract_wordpress_schemas.DATA_DIR", tmp_path):
        await fetch_schema(mock_client, "TEST_SCHEMA.json", "/wp-json/wc/v3/test")

    assert target_file.exists()
    content = json.loads(target_file.read_text(encoding="utf-8"))
    assert content["namespace"] == "wc/v3"


def test_extracted_schema_files_exist_and_valid_json():
    # File is at packages/woocommerce-event/tests/unit/scripts/test_extract_wordpress_schemas.py
    # parents[0] = scripts, [1] = unit, [2] = tests, [3] = woocommerce-event, [4] = packages, [5] = root
    test_file = Path(__file__).resolve()
    data_path = test_file.parents[5] / "data"
    for file_name in ENDPOINTS:
        file_path = data_path / file_name
        assert file_path.exists(), f"Schema file {file_name} should exist in data/"
        content = json.loads(file_path.read_text(encoding="utf-8"))
        assert isinstance(content, dict), f"{file_name} should contain a JSON dict"
