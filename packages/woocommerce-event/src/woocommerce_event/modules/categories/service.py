"""Category domain transformation and service execution logic."""

import uuid
from datetime import UTC, datetime
from typing import Any

import structlog

from woocommerce_event.integrations.woocommerce import WooCommerceClient
from woocommerce_event.modules.categories.schemas import (
    Category,
    CategoryCreated,
    CategoryDeleted,
    CategoryUpdated,
)

logger = structlog.get_logger(__name__)


def parse_category_webhook(
    raw_json: dict[str, Any],
    tenant_id: int | str,
    site_id: int | str = 1,
    action: str = "created",
) -> CategoryCreated | CategoryUpdated | CategoryDeleted:
    """Parse raw category webhook payload into a canonical CloudEvent."""
    logger.debug(
        "Parsing category webhook payload",
        tenant_id=tenant_id,
        site_id=site_id,
        category_id=raw_json.get("id"),
    )

    category = Category.model_validate(raw_json)
    event_id = str(uuid.uuid4())
    now = datetime.now(UTC)
    source = f"woocommerce://{site_id}/categories"
    subject = str(site_id)

    if action == "deleted":
        logger.info(
            "Created CategoryDeleted event",
            event_id=event_id,
            category_id=category.id,
            tenant_id=tenant_id,
        )
        return CategoryDeleted(
            id=event_id,
            source=source,
            subject=subject,
            time=now,
            tenant_id=tenant_id,
            data=category,
        )
    elif action == "updated":
        logger.info(
            "Created CategoryUpdated event",
            event_id=event_id,
            category_id=category.id,
            tenant_id=tenant_id,
        )
        return CategoryUpdated(
            id=event_id,
            source=source,
            subject=subject,
            time=now,
            tenant_id=tenant_id,
            data=category,
        )

    logger.info(
        "Created CategoryCreated event",
        event_id=event_id,
        category_id=category.id,
        tenant_id=tenant_id,
    )
    return CategoryCreated(
        id=event_id,
        source=source,
        subject=subject,
        time=now,
        tenant_id=tenant_id,
        data=category,
    )


async def upsert_category(
    client: WooCommerceClient, category: Category
) -> dict[str, Any]:
    """Upsert category in WooCommerce store with clean 1:1 serialization."""
    logger.info("Upserting category in WooCommerce", name=category.name)
    body = category.model_dump(exclude_unset=True, exclude_none=True)

    if category.id:
        result = await client.update_category(category.id, body)
        logger.info("Category updated successfully", category_id=category.id)
    else:
        result = await client.create_category(body)
        logger.info("Category created successfully", category_id=result.get("id"))

    return result


submit_category = upsert_category

__all__ = ["parse_category_webhook", "submit_category", "upsert_category"]
