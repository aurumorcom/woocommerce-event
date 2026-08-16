"""Tag domain transformation and service execution logic."""

import uuid
from datetime import UTC, datetime
from typing import Any

import structlog

from woocommerce_event.integrations.woocommerce import WooCommerceClient
from woocommerce_event.modules.tags.schemas import (
    Tag,
    TagCreated,
    TagDeleted,
    TagUpdated,
)

logger = structlog.get_logger(__name__)


def parse_tag_webhook(
    raw_json: dict[str, Any],
    tenant_id: int | str,
    site_id: int | str = 1,
    action: str = "created",
) -> TagCreated | TagUpdated | TagDeleted:
    """Parse raw tag webhook payload into a canonical CloudEvent."""
    logger.debug(
        "Parsing tag webhook payload",
        tenant_id=tenant_id,
        site_id=site_id,
        tag_id=raw_json.get("id"),
    )

    tag = Tag.model_validate(raw_json)
    event_id = str(uuid.uuid4())
    now = datetime.now(UTC)
    source = f"woocommerce://{site_id}/tags"
    subject = str(site_id)

    if action == "deleted":
        logger.info(
            "Created TagDeleted event",
            event_id=event_id,
            tag_id=tag.id,
            tenant_id=tenant_id,
        )
        return TagDeleted(
            id=event_id,
            source=source,
            subject=subject,
            time=now,
            tenant_id=tenant_id,
            data=tag,
        )
    elif action == "updated":
        logger.info(
            "Created TagUpdated event",
            event_id=event_id,
            tag_id=tag.id,
            tenant_id=tenant_id,
        )
        return TagUpdated(
            id=event_id,
            source=source,
            subject=subject,
            time=now,
            tenant_id=tenant_id,
            data=tag,
        )

    logger.info(
        "Created TagCreated event",
        event_id=event_id,
        tag_id=tag.id,
        tenant_id=tenant_id,
    )
    return TagCreated(
        id=event_id,
        source=source,
        subject=subject,
        time=now,
        tenant_id=tenant_id,
        data=tag,
    )


async def upsert_tag(client: WooCommerceClient, tag: Tag) -> dict[str, Any]:
    """Upsert tag in WooCommerce store with clean 1:1 serialization."""
    logger.info("Upserting tag to WooCommerce", name=tag.name)
    body = tag.model_dump(exclude_unset=True, exclude_none=True)

    if tag.id:
        result = await client.update_tag(tag.id, body)
        logger.info("Tag updated successfully", tag_id=tag.id)
    else:
        result = await client.create_tag(body)
        logger.info("Tag created successfully", tag_id=result.get("id"))

    return result


submit_tag = upsert_tag

__all__ = ["parse_tag_webhook", "submit_tag", "upsert_tag"]
