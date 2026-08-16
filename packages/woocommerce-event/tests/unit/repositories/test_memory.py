"""Unit tests for in-memory repositories."""

import pytest
from woocommerce_event.exceptions import CredentialsNotFoundError
from woocommerce_event.repositories.memory import (
    MemoryCredentialsRepository,
    MemoryStateRepository,
)
from woocommerce_event.schemas import Credentials


@pytest.mark.asyncio
async def test_memory_credentials_repository():
    """Test saving and retrieving credentials in MemoryCredentialsRepository."""
    repo = MemoryCredentialsRepository()
    creds = Credentials(
        site_url="https://site.com", consumer_key="ck", consumer_secret="cs"
    )
    repo.add_credentials(1, 101, creds)

    retrieved = await repo.get_credentials(1, 101)
    assert retrieved.site_url == "https://site.com"

    # Test string ID normalization
    retrieved_str = await repo.get_credentials("1", "101")
    assert retrieved_str.site_url == "https://site.com"

    with pytest.raises(CredentialsNotFoundError):
        await repo.get_credentials(999, 101)


@pytest.mark.asyncio
async def test_memory_state_repository_ttl():
    """Test setting, retrieving, and expiring state in MemoryStateRepository."""
    repo = MemoryStateRepository()
    await repo.set_state("key1", "val1", ttl_seconds=3600)
    val = await repo.get_state("key1")
    assert val == "val1"

    # Test expired
    await repo.set_state("key2", "val2", ttl_seconds=-1)
    val2 = await repo.get_state("key2")
    assert val2 is None
