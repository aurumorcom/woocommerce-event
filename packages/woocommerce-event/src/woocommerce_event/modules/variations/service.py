"""Variation domain transformation and service execution logic."""

import uuid
from datetime import UTC, datetime
from typing import Any

import structlog

from woocommerce_event.integrations.woocommerce import WooCommerceClient
from woocommerce_event.modules.variations.schemas import (
    Variation,
    VariationCreated,
    VariationDeleted,
    VariationUpdated,
)

logger = structlog.get_logger(__name__)


def parse_variation_webhook(
    raw_json: dict[str, Any],
    parent_id: int,
    tenant_id: int | str,
    site_id: int | str = 1,
    action: str = "created",
) -> VariationCreated | VariationUpdated | VariationDeleted:
    """Parse raw variation webhook payload into a canonical CloudEvent."""
    logger.debug(
        "Parsing variation webhook payload",
        parent_id=parent_id,
        tenant_id=tenant_id,
        site_id=site_id,
        variation_id=raw_json.get("id"),
    )

    data_payload = {**raw_json, "parent_id": parent_id}
    variation = Variation.model_validate(data_payload)
    event_id = str(uuid.uuid4())
    now = datetime.now(UTC)
    source = f"woocommerce://{site_id}/products/{parent_id}/variations"
    subject = str(site_id)

    if action == "deleted":
        logger.info(
            "Created VariationDeleted event",
            event_id=event_id,
            variation_id=variation.id,
            parent_id=parent_id,
            tenant_id=tenant_id,
        )
        return VariationDeleted(
            id=event_id,
            source=source,
            subject=subject,
            time=now,
            tenant_id=tenant_id,
            data=variation,
        )
    elif action == "updated":
        logger.info(
            "Created VariationUpdated event",
            event_id=event_id,
            variation_id=variation.id,
            parent_id=parent_id,
            tenant_id=tenant_id,
        )
        return VariationUpdated(
            id=event_id,
            source=source,
            subject=subject,
            time=now,
            tenant_id=tenant_id,
            data=variation,
        )

    logger.info(
        "Created VariationCreated event",
        event_id=event_id,
        variation_id=variation.id,
        parent_id=parent_id,
        tenant_id=tenant_id,
    )
    return VariationCreated(
        id=event_id,
        source=source,
        subject=subject,
        time=now,
        tenant_id=tenant_id,
        data=variation,
    )


async def upsert_variation(
    client: WooCommerceClient, product_id: int, variation: Variation
) -> dict[str, Any]:
    """Upsert variation to WooCommerce via REST API with clean 1:1 serialization."""
    logger.info(
        "Upserting variation to WooCommerce",
        product_id=product_id,
        sku=variation.sku,
    )
    body = variation.model_dump(exclude_unset=True, exclude_none=True)
    body.pop("parent_id", None)

    if variation.id:
        result = await client.update_variation(product_id, variation.id, body)
        logger.info(
            "Variation updated successfully",
            product_id=product_id,
            variation_id=variation.id,
        )
    else:
        result = await client.create_variation(product_id, body)
        logger.info(
            "Variation created successfully",
            product_id=product_id,
            variation_id=result.get("id"),
        )

    return result


submit_variation = upsert_variation

__all__ = ["parse_variation_webhook", "submit_variation", "upsert_variation"]


__all__ = ["parse_variation_webhook", "submit_variation"]
