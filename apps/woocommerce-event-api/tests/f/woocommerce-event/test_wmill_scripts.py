"""Unit tests for Windmill scripts in apps/woocommerce-event-api/f/woocommerce-event/."""

import importlib.util
import sys
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

test_file = Path(__file__).resolve()
workspace_root = (
    test_file.parents[4]
    if (test_file.parents[4] / "packages").exists()
    else test_file.parents[5]
)
app_dir = (
    test_file.parents[3]
    if (test_file.parents[3] / "f").exists()
    else test_file.parents[2]
)

for p in [
    workspace_root,
    workspace_root / "packages" / "woocommerce-event" / "src",
    workspace_root / "packages" / "woocommerce-event" / "tests",
    workspace_root / ".agents/skills/python-event/modules/python-event/src",
    workspace_root / ".agents/skills/python-logging/modules/python-logging/src",
]:
    p_str = str(p.resolve())
    if p_str not in sys.path:
        sys.path.insert(0, p_str)

# Mock confluent_kafka in sys.modules if not installed
if "confluent_kafka" not in sys.modules:
    mock_ck = MagicMock()
    mock_ck.KafkaException = Exception
    mock_producer_instance = MagicMock()
    mock_producer_instance.flush.return_value = 0
    mock_ck.Producer.return_value = mock_producer_instance
    sys.modules["confluent_kafka"] = mock_ck

if "psycopg2" not in sys.modules:
    sys.modules["psycopg2"] = MagicMock()

if "fastavro" not in sys.modules:
    sys.modules["fastavro"] = MagicMock()

fixtures_file = (
    workspace_root
    / "packages"
    / "woocommerce-event"
    / "tests"
    / "fixtures"
    / "woocommerce_api_samples.py"
)

# Load fixtures module
spec_fix = importlib.util.spec_from_file_location("samples_fixture", fixtures_file)
assert spec_fix is not None and spec_fix.loader is not None
samples_mod = importlib.util.module_from_spec(spec_fix)
spec_fix.loader.exec_module(samples_mod)

SAMPLE_PRODUCT_RAW = samples_mod.SAMPLE_PRODUCT_RAW
SAMPLE_VARIATION_RAW = samples_mod.SAMPLE_VARIATION_RAW
SAMPLE_ORDER_RAW = samples_mod.SAMPLE_ORDER_RAW
SAMPLE_CATEGORY_RAW = samples_mod.SAMPLE_CATEGORY_RAW
SAMPLE_TAG_RAW = samples_mod.SAMPLE_TAG_RAW
SAMPLE_ATTRIBUTE_RAW = samples_mod.SAMPLE_ATTRIBUTE_RAW
SAMPLE_MEDIA_RAW = samples_mod.SAMPLE_MEDIA_RAW

wmill_dir = app_dir / "f" / "woocommerce-event"

import pytest
from python_event.client import EventClient, PublishResponse


@pytest.fixture(autouse=True)
def mock_kafka_publisher(monkeypatch):
    """Mock EventClient and confluent_kafka Producer for offline testing."""

    async def fake_publish(
        self,
        topic: str,
        event: Any,
        schema_id: int | None = None,
        key: str | None = None,
        headers: dict | None = None,
        **kwargs,
    ):
        partition_key = key or getattr(event, "subject", "default")
        return PublishResponse(
            topic=topic,
            event_id=getattr(event, "id", "evt-mock-id"),
            partition_key=str(partition_key),
            status="published",
            timestamp=123456789.0,
        )

    async def fake_provision(self, *args, **kwargs):
        return None

    async def fake_aclose(self):
        return None

    monkeypatch.setattr(EventClient, "apublish_event", fake_publish)
    monkeypatch.setattr(EventClient, "aprovision_topology", fake_provision)
    monkeypatch.setattr(EventClient, "aclose", fake_aclose)


def load_wmill_script(script_name: str):
    script_path = wmill_dir / f"{script_name}.py"
    spec = importlib.util.spec_from_file_location(script_name, script_path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.mark.asyncio
async def test_wm_products_script():
    """Test Windmill products script webhook handling."""
    mod = load_wmill_script("products")
    payload = {
        "action_type": "webhook",
        "tenant_id": 1,
        "site_id": 101,
        "data": SAMPLE_PRODUCT_RAW,
    }
    result = await mod.amain(payload)
    assert result["status"] == "published"


@pytest.mark.asyncio
async def test_wm_variations_script():
    """Test Windmill variations script webhook handling."""
    mod = load_wmill_script("variations")
    payload = {
        "action_type": "webhook",
        "tenant_id": 1,
        "site_id": 101,
        "parent_id": 799,
        "data": SAMPLE_VARIATION_RAW,
    }
    result = await mod.amain(payload)
    assert result["status"] == "published"


@pytest.mark.asyncio
async def test_wm_orders_script():
    """Test Windmill orders script webhook handling."""
    mod = load_wmill_script("orders")
    payload = {
        "action_type": "webhook",
        "tenant_id": 1,
        "site_id": 101,
        "data": SAMPLE_ORDER_RAW,
    }
    result = await mod.amain(payload)
    assert result["status"] == "published"


@pytest.mark.asyncio
async def test_wm_categories_script():
    """Test Windmill categories script webhook handling."""
    mod = load_wmill_script("categories")
    payload = {
        "action_type": "webhook",
        "tenant_id": 1,
        "site_id": 101,
        "data": SAMPLE_CATEGORY_RAW,
    }
    result = await mod.amain(payload)
    assert result["status"] == "published"


@pytest.mark.asyncio
async def test_wm_tags_script():
    """Test Windmill tags script webhook handling."""
    mod = load_wmill_script("tags")
    payload = {
        "action_type": "webhook",
        "tenant_id": 1,
        "site_id": 101,
        "data": SAMPLE_TAG_RAW,
    }
    result = await mod.amain(payload)
    assert result["status"] == "published"


@pytest.mark.asyncio
async def test_wm_attributes_script():
    """Test Windmill attributes script webhook handling."""
    mod = load_wmill_script("attributes")
    payload = {
        "action_type": "webhook",
        "tenant_id": 1,
        "site_id": 101,
        "data": SAMPLE_ATTRIBUTE_RAW,
    }
    result = await mod.amain(payload)
    assert result["status"] == "published"


@pytest.mark.asyncio
async def test_wm_media_script():
    """Test Windmill media script webhook handling."""
    mod = load_wmill_script("media")
    payload = {
        "action_type": "webhook",
        "tenant_id": 1,
        "site_id": 101,
        "data": SAMPLE_MEDIA_RAW,
    }
    result = await mod.amain(payload)
    assert result["status"] == "published"


@pytest.mark.asyncio
async def test_wm_webhooks_script():
    """Test Windmill webhooks script signature verification."""
    mod = load_wmill_script("webhooks")
    payload = {
        "action_type": "verify_signature",
        "raw_body": '{"test": 1}',
        "signature": "fake",
        "secret": "secret",
    }
    result = await mod.amain(payload)
    assert "valid" in result


@pytest.mark.asyncio
async def test_wm_sites_script():
    """Test Windmill sites provisioning script."""
    mod = load_wmill_script("sites")
    payload = {
        "action_type": "provision",
        "tenant_id": 1,
        "site_id": 101,
        "environment": "staging",
    }
    result = await mod.amain(payload)
    assert result["status"] == "provisioned"
    assert result["tenant_id"] == 1
    assert result["site_id"] == 101
