"""Unit tests for site provisioning service."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from woocommerce_event.constants import TOPIC_CHANNEL
from woocommerce_event.modules.sites.schemas import ChannelCreated
from woocommerce_event.modules.sites.service import register_site_topology
from woocommerce_event.schemas import Site


@pytest.mark.asyncio
async def test_register_site_topology():
    """Test registering site streaming topology."""
    mock_client = MagicMock()
    mock_client.event_client = MagicMock()
    mock_client.event_client.aprovision_topology = AsyncMock()

    ctx = Site(tenant_id=1, site_id=101, environment="production")
    await register_site_topology(mock_client, ctx)

    mock_client.event_client.aprovision_topology.assert_awaited_once_with(
        event_cls=ChannelCreated,
        topic=TOPIC_CHANNEL,
    )
