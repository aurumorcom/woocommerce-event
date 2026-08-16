"""Unit tests for protocol adherence."""

from woocommerce_event.protocols import CredentialsRepository, StateRepository
from woocommerce_event.repositories.memory import (
    MemoryCredentialsRepository,
    MemoryStateRepository,
)


def test_memory_implements_credentials_repository():
    """Verify MemoryCredentialsRepository implements CredentialsRepository."""
    repo = MemoryCredentialsRepository()
    assert isinstance(repo, CredentialsRepository)


def test_memory_implements_state_repository():
    """Verify MemoryStateRepository implements StateRepository."""
    repo = MemoryStateRepository()
    assert isinstance(repo, StateRepository)
