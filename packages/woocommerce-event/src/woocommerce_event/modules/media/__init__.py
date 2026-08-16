"""Media domain module."""

from woocommerce_event.modules.media import schemas, service
from woocommerce_event.modules.media.schemas import (
    MediaCreated,
    MediaDeleted,
    MediaDetails,
    MediaItem,
    MediaUpdated,
)
from woocommerce_event.modules.media.service import (
    parse_media_webhook,
    upload_media,
)

__all__ = [
    "MediaCreated",
    "MediaDeleted",
    "MediaDetails",
    "MediaItem",
    "MediaUpdated",
    "parse_media_webhook",
    "schemas",
    "service",
    "upload_media",
]
