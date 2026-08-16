"""Internal integration tests for Windmill repositories."""

import pytest
from woocommerce_event.repositories.windmill import WindmillStateRepository


@pytest.mark.asyncio
async def test_windmill_state_repository_integration():
    """Test state storage and retrieval lifecycle."""
    repo = WindmillStateRepository()
    await repo.set_state("order_nonce_123", "processed")
    status = await repo.get_state("order_nonce_123")
    assert status == "processed"
