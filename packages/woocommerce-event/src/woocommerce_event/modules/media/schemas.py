"""WordPress/WooCommerce Media domain schemas and CloudEvents definitions."""

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field
from python_event.modules.events.schemas import EventBaseModel, EventData

from woocommerce_event.constants import (
    EVENT_TYPE_MEDIA_CREATED,
    EVENT_TYPE_MEDIA_DELETED,
    EVENT_TYPE_MEDIA_UPDATED,
)


class MediaDetails(BaseModel):
    """Media image/attachment detailed dimensions and metadata."""

    width: int | None = Field(default=None, description="Image width")
    height: int | None = Field(default=None, description="Image height")
    file: str | None = Field(default=None, description="File path")
    filesize: int | None = Field(default=None, description="File size in bytes")


class MediaItem(EventData):
    """1:1 WordPress REST API Media Object."""

    id: int | None = Field(default=None, description="Media attachment ID")
    date: str | None = Field(default=None, description="Publish date")
    slug: str | None = Field(default=None, description="Media slug")
    type: str = Field(default="attachment", description="Post type")
    link: str | None = Field(default=None, description="Attachment page URL")
    title: dict[str, Any] | None = Field(default=None, description="Media title object")
    author: int | None = Field(default=None, description="Author user ID")
    source_url: str | None = Field(
        default=None, description="Original media source URL"
    )
    media_type: str = Field(
        default="image", description="Type of media (image, file, video)"
    )
    mime_type: str | None = Field(default=None, description="MIME type")
    media_details: MediaDetails | None = Field(
        default=None, description="Detailed metadata"
    )


class MediaCreated(EventBaseModel):
    """CloudEvent emitted when a media item is uploaded/created."""

    type: str = Field(default=EVENT_TYPE_MEDIA_CREATED, description="CloudEvents type")
    source: str = Field(
        default="woocommerce://1/media", description="Context URI reference"
    )
    subject: str = Field(default="1", description="Numeric site identifier")
    time: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Event timestamp",
    )
    tenant_id: int | str = Field(
        default="default", description="Dedicated tenant extension attribute"
    )
    data: MediaItem = Field(description="Media data payload")


class MediaUpdated(EventBaseModel):
    """CloudEvent emitted when a media item is updated."""

    type: str = Field(default=EVENT_TYPE_MEDIA_UPDATED, description="CloudEvents type")
    source: str = Field(
        default="woocommerce://1/media", description="Context URI reference"
    )
    subject: str = Field(default="1", description="Numeric site identifier")
    time: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Event timestamp",
    )
    tenant_id: int | str = Field(
        default="default", description="Dedicated tenant extension attribute"
    )
    data: MediaItem = Field(description="Media data payload")


class MediaDeleted(EventBaseModel):
    """CloudEvent emitted when a media item is deleted."""

    type: str = Field(default=EVENT_TYPE_MEDIA_DELETED, description="CloudEvents type")
    source: str = Field(
        default="woocommerce://1/media", description="Context URI reference"
    )
    subject: str = Field(default="1", description="Numeric site identifier")
    time: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Event timestamp",
    )
    tenant_id: int | str = Field(
        default="default", description="Dedicated tenant extension attribute"
    )
    data: MediaItem = Field(description="Media data payload")


Media = MediaItem

__all__ = [
    "Media",
    "MediaCreated",
    "MediaDeleted",
    "MediaDetails",
    "MediaItem",
    "MediaUpdated",
]
