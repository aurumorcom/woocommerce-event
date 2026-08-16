"""Unit tests for site provisioning schemas."""

from datetime import UTC, datetime

from woocommerce_event.modules.sites.schemas import (
    ChannelCreated,
    ChannelDeleted,
    ChannelUpdated,
)
from woocommerce_event.schemas import Site


def test_site_provisioned_event():
    """Test ChannelCreated CloudEvent schema."""
    ctx = Site(tenant_id=1, site_id=101, environment="production")
    event = ChannelCreated(
        id="evt-site-1",
        source="woocommerce://101/sites",
        subject="101",
        time=datetime.now(UTC),
        tenant_id=1,
        data=ctx,
    )
    assert event.type == "channel.created"
    assert event.subject == "101"
    assert event.tenant_id == 1
    assert event.data.tenant_id == 1
    assert event.data.site_id == 101


def test_channel_updated_event():
    """Test ChannelUpdated CloudEvent schema."""
    ctx = Site(tenant_id=1, site_id=101, environment="production")
    event = ChannelUpdated(
        id="evt-site-update",
        source="woocommerce://101/sites",
        subject="101",
        time=datetime.now(UTC),
        tenant_id=1,
        data=ctx,
    )
    assert event.type == "channel.updated"
    assert event.subject == "101"


def test_site_decommissioned_event():
    """Test ChannelDeleted CloudEvent schema."""
    ctx = Site(tenant_id=1, site_id=101, environment="production")
    event = ChannelDeleted(
        id="evt-site-2",
        source="woocommerce://101/sites",
        subject="101",
        time=datetime.now(UTC),
        tenant_id=1,
        data=ctx,
    )
    assert event.type == "channel.deleted"
    assert event.subject == "101"
