"""Shared pytest fixtures and test configurations."""

import os
import sys
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

# Ensure root workspace, packages, and local skill dependencies are in sys.path
tests_dir = Path(__file__).resolve().parent
pkg_dir = tests_dir.parents[0]
root_dir = (
    tests_dir.parents[1]
    if len(tests_dir.parents) > 1 and (tests_dir.parents[1] / ".agents").exists()
    else tests_dir.parents[2]
)

for p in [
    root_dir,
    pkg_dir,
    pkg_dir / "src",
    tests_dir,
    root_dir / ".agents/skills/python-event/modules/python-event/src",
    root_dir / ".agents/skills/python-logging/modules/python-logging/src",
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

# Mock psycopg2 in sys.modules if not installed
if "psycopg2" not in sys.modules:
    sys.modules["psycopg2"] = MagicMock()

# Mock fastavro in sys.modules if not installed
if "fastavro" not in sys.modules:
    sys.modules["fastavro"] = MagicMock()

import pytest
from python_event.client import EventClient, PublishResponse
from structlog.testing import capture_logs
from woocommerce_event.repositories.memory import (
    MemoryCredentialsRepository,
    MemoryStateRepository,
)
from woocommerce_event.schemas import Credentials


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
        partition_key = key
        if partition_key is None and hasattr(event, "tenant_id"):
            partition_key = str(event.tenant_id)
        if partition_key is None and hasattr(event, "subject"):
            partition_key = str(event.subject)
        if partition_key is None:
            partition_key = "default"
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


@pytest.fixture
def captured_logs():
    """Fixture capturing all structlog emissions for assertion."""
    with capture_logs() as cap_logs:
        yield cap_logs


@pytest.fixture
def sample_credentials() -> Credentials:
    """Fixture providing standard test credentials."""
    return Credentials(
        site_url="https://store.example.com",
        consumer_key="ck_test_1234567890",
        consumer_secret="cs_test_0987654321",
    )


@pytest.fixture
def memory_credentials_repo(
    sample_credentials: Credentials,
) -> MemoryCredentialsRepository:
    """Fixture providing populated in-memory credentials repository."""
    repo = MemoryCredentialsRepository()
    repo.add_credentials(1, 101, sample_credentials)
    return repo


@pytest.fixture
def memory_state_repo() -> MemoryStateRepository:
    """Fixture providing empty in-memory state repository."""
    return MemoryStateRepository()


@pytest.fixture
def live_credentials() -> Credentials:
    """Fixture providing live or sandbox WooCommerce credentials from settings/environment."""
    from woocommerce_event.config import Settings

    s = Settings()
    site_url = s.woocommerce.site_url or os.environ.get(
        "WOOCOMMERCE_SITE_URL", "https://badsyxn.capybaara.com"
    )
    consumer_key = s.woocommerce.consumer_key or os.environ.get(
        "WOOCOMMERCE_CONSUMER_KEY", "aquiveal"
    )
    consumer_secret = s.woocommerce.consumer_secret or os.environ.get(
        "WOOCOMMERCE_CONSUMER_SECRET", "8Gv1hUJTxhGOnUftuuNo"
    )
    return Credentials(
        site_url=site_url,
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
    )
