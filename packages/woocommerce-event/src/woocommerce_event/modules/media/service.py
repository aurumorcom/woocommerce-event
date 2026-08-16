"""Media domain transformation and service execution logic."""

import uuid
from datetime import UTC, datetime
from typing import Any

import structlog

from woocommerce_event.integrations.woocommerce import WooCommerceClient
from woocommerce_event.modules.media.schemas import (
    MediaCreated,
    MediaDeleted,
    MediaItem,
    MediaUpdated,
)

logger = structlog.get_logger(__name__)


def parse_media_webhook(
    raw_json: dict[str, Any],
    tenant_id: int | str,
    site_id: int | str = 1,
    action: str = "created",
) -> MediaCreated | MediaUpdated | MediaDeleted:
    """Parse raw WordPress/WooCommerce media webhook payload into a canonical CloudEvent."""
    logger.debug(
        "Parsing media webhook payload",
        tenant_id=tenant_id,
        site_id=site_id,
        media_id=raw_json.get("id"),
    )

    media = MediaItem.model_validate(raw_json)
    event_id = str(uuid.uuid4())
    now = datetime.now(UTC)
    source = f"woocommerce://{site_id}/media"
    subject = str(site_id)

    if action == "deleted":
        logger.info(
            "Created MediaDeleted event",
            event_id=event_id,
            media_id=media.id,
            tenant_id=tenant_id,
        )
        return MediaDeleted(
            id=event_id,
            source=source,
            subject=subject,
            time=now,
            tenant_id=tenant_id,
            data=media,
        )
    elif action == "updated":
        logger.info(
            "Created MediaUpdated event",
            event_id=event_id,
            media_id=media.id,
            tenant_id=tenant_id,
        )
        return MediaUpdated(
            id=event_id,
            source=source,
            subject=subject,
            time=now,
            tenant_id=tenant_id,
            data=media,
        )

    logger.info(
        "Created MediaCreated event",
        event_id=event_id,
        media_id=media.id,
        tenant_id=tenant_id,
    )
    return MediaCreated(
        id=event_id,
        source=source,
        subject=subject,
        time=now,
        tenant_id=tenant_id,
        data=media,
    )


async def upload_media(
    client: WooCommerceClient,
    filename: str,
    content_type: str,
    data: bytes,
) -> MediaItem:
    """Upload media binary to WordPress/WooCommerce media library."""
    logger.info(
        "Uploading media binary to WordPress/WooCommerce",
        filename=filename,
        content_type=content_type,
        size=len(data),
    )
    raw_resp = await client.create_media(
        filename=filename, content_type=content_type, data=data
    )
    media_item = MediaItem.model_validate(raw_resp)
    logger.info(
        "Media uploaded successfully",
        media_id=media_item.id,
        source_url=media_item.source_url,
    )
    return media_item


__all__ = ["parse_media_webhook", "upload_media"]
