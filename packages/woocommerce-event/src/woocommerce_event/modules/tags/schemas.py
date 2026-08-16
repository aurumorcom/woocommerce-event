"""Tag domain schemas and CloudEvents definitions."""

from datetime import UTC, datetime

from pydantic import Field
from python_event.modules.events.schemas import EventBaseModel, EventData

from woocommerce_event.constants import (
    EVENT_TYPE_ITEM_TAG_CREATED,
    EVENT_TYPE_ITEM_TAG_DELETED,
    EVENT_TYPE_ITEM_TAG_UPDATED,
)


class Tag(EventData):
    """1:1 WooCommerce Product Tag Model."""

    id: int | None = Field(default=None, description="Tag ID")
    name: str = Field(description="Tag name")
    slug: str | None = Field(default=None, description="Tag URL slug")
    description: str | None = Field(default=None, description="Tag description")
    count: int = Field(default=0, description="Number of products with this tag")


class TagCreated(EventBaseModel):
    """CloudEvent emitted when a product tag is created."""

    type: str = Field(
        default=EVENT_TYPE_ITEM_TAG_CREATED, description="CloudEvents type"
    )
    source: str = Field(
        default="woocommerce://1/tags", description="Context URI reference"
    )
    subject: str = Field(default="1", description="Numeric site identifier")
    time: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Event timestamp",
    )
    tenant_id: int | str = Field(
        default="default", description="Dedicated tenant extension attribute"
    )
    data: Tag = Field(description="Tag data payload")


class TagUpdated(EventBaseModel):
    """CloudEvent emitted when a product tag is updated."""

    type: str = Field(
        default=EVENT_TYPE_ITEM_TAG_UPDATED, description="CloudEvents type"
    )
    source: str = Field(
        default="woocommerce://1/tags", description="Context URI reference"
    )
    subject: str = Field(default="1", description="Numeric site identifier")
    time: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Event timestamp",
    )
    tenant_id: int | str = Field(
        default="default", description="Dedicated tenant extension attribute"
    )
    data: Tag = Field(description="Tag data payload")


class TagDeleted(EventBaseModel):
    """CloudEvent emitted when a product tag is deleted."""

    type: str = Field(
        default=EVENT_TYPE_ITEM_TAG_DELETED, description="CloudEvents type"
    )
    source: str = Field(
        default="woocommerce://1/tags", description="Context URI reference"
    )
    subject: str = Field(default="1", description="Numeric site identifier")
    time: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Event timestamp",
    )
    tenant_id: int | str = Field(
        default="default", description="Dedicated tenant extension attribute"
    )
    data: Tag = Field(description="Tag data payload")


ItemTag = Tag

__all__ = ["ItemTag", "Tag", "TagCreated", "TagDeleted", "TagUpdated"]
