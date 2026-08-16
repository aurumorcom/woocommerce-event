"""Product domain transformation and service execution logic."""

import uuid
from datetime import UTC, datetime
from typing import Any

import structlog

from woocommerce_event.integrations.woocommerce import WooCommerceClient
from woocommerce_event.modules.products.schemas import (
    Product,
    ProductCreated,
    ProductDeleted,
    ProductUpdated,
)

logger = structlog.get_logger(__name__)


def parse_product_webhook(
    raw_json: dict[str, Any],
    tenant_id: int | str,
    site_id: int | str = 1,
    action: str = "created",
) -> ProductCreated | ProductUpdated | ProductDeleted:
    """Parse WooCommerce product webhook payload into a canonical CloudEvent."""
    logger.debug(
        "Parsing product webhook payload",
        tenant_id=tenant_id,
        site_id=site_id,
        product_id=raw_json.get("id"),
    )

    product = Product.model_validate(raw_json)
    event_id = str(uuid.uuid4())
    now = datetime.now(UTC)
    source = f"woocommerce://{site_id}/products"
    subject = str(site_id)

    if action == "deleted":
        logger.info(
            "Created ProductDeleted event",
            event_id=event_id,
            sku=product.sku,
            tenant_id=tenant_id,
        )
        return ProductDeleted(
            id=event_id,
            source=source,
            subject=subject,
            time=now,
            tenant_id=tenant_id,
            data=product,
        )
    elif action == "updated":
        logger.info(
            "Created ProductUpdated event",
            event_id=event_id,
            sku=product.sku,
            tenant_id=tenant_id,
        )
        return ProductUpdated(
            id=event_id,
            source=source,
            subject=subject,
            time=now,
            tenant_id=tenant_id,
            data=product,
        )

    logger.info(
        "Created ProductCreated event",
        event_id=event_id,
        sku=product.sku,
        tenant_id=tenant_id,
    )
    return ProductCreated(
        id=event_id,
        source=source,
        subject=subject,
        time=now,
        tenant_id=tenant_id,
        data=product,
    )


async def upsert_product(client: WooCommerceClient, product: Product) -> dict[str, Any]:
    """Upsert product to WooCommerce store via REST API with clean 1:1 serialization."""
    logger.info(
        "Upserting product to WooCommerce store",
        sku=product.sku,
        name=product.name,
    )

    body = product.model_dump(exclude_unset=True, exclude_none=True)

    if product.id:
        result = await client.update_product(
            product_id=product.id,
            body=body,
        )
    else:
        result = await client.create_product(body=body)

    logger.info(
        "Product upsert successful",
        sku=product.sku,
        wc_product_id=result.get("id"),
    )
    return result


submit_product = upsert_product

__all__ = ["parse_product_webhook", "submit_product", "upsert_product"]
