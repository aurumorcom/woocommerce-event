"""Site/Channel multi-tenant provisioning schemas and CloudEvents definitions."""

from datetime import UTC, datetime

from pydantic import Field
from python_event.modules.events.schemas import EventBaseModel

from woocommerce_event.constants import (
    EVENT_TYPE_CHANNEL_CREATED,
    EVENT_TYPE_CHANNEL_DELETED,
    EVENT_TYPE_CHANNEL_UPDATED,
)
from woocommerce_event.schemas import Site


class ChannelCreated(EventBaseModel):
    """CloudEvent emitted when a store channel/site is provisioned."""

    type: str = Field(
        default=EVENT_TYPE_CHANNEL_CREATED, description="CloudEvents type"
    )
    subject: str = Field(default="1", description="Numeric site identifier")
    time: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Event timestamp",
    )
    tenant_id: int | str = Field(
        default="default", description="Dedicated tenant extension attribute"
    )
    data: Site = Field(description="Channel / Site context payload")


class ChannelUpdated(EventBaseModel):
    """CloudEvent emitted when a store channel/site is updated."""

    type: str = Field(
        default=EVENT_TYPE_CHANNEL_UPDATED, description="CloudEvents type"
    )
    subject: str = Field(default="1", description="Numeric site identifier")
    time: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Event timestamp",
    )
    tenant_id: int | str = Field(
        default="default", description="Dedicated tenant extension attribute"
    )
    data: Site = Field(description="Channel / Site context payload")


class ChannelDeleted(EventBaseModel):
    """CloudEvent emitted when a store channel/site is decommissioned/deleted."""

    type: str = Field(
        default=EVENT_TYPE_CHANNEL_DELETED, description="CloudEvents type"
    )
    subject: str = Field(default="1", description="Numeric site identifier")
    time: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Event timestamp",
    )
    tenant_id: int | str = Field(
        default="default", description="Dedicated tenant extension attribute"
    )
    data: Site = Field(description="Channel / Site context payload")


SiteProvisioned = ChannelCreated
SiteDecommissioned = ChannelDeleted

__all__ = [
    "ChannelCreated",
    "ChannelDeleted",
    "ChannelUpdated",
    "SiteDecommissioned",
    "SiteProvisioned",
]
