"""Order domain transformation and service execution logic."""

import uuid
from datetime import UTC, datetime
from typing import Any

import structlog

from woocommerce_event.integrations.woocommerce import WooCommerceClient
from woocommerce_event.modules.orders.schemas import (
    Order,
    OrderCancelled,
    OrderCreated,
    OrderUpdated,
)

logger = structlog.get_logger(__name__)


def parse_order_webhook(
    raw_json: dict[str, Any],
    tenant_id: int | str,
    site_id: int | str = 1,
    action: str = "created",
) -> OrderCreated | OrderUpdated | OrderCancelled:
    """Parse raw order webhook payload into a canonical CloudEvent."""
    logger.debug(
        "Parsing order webhook payload",
        tenant_id=tenant_id,
        site_id=site_id,
        order_id=raw_json.get("id"),
        action=action,
    )

    order = Order.model_validate(raw_json)
    event_id = str(uuid.uuid4())
    now = datetime.now(UTC)
    source = f"woocommerce://{site_id}/orders"
    subject = str(site_id)

    if action == "cancelled" or order.status == "cancelled":
        logger.info(
            "Created OrderCancelled event",
            event_id=event_id,
            order_id=order.id,
            tenant_id=tenant_id,
        )
        return OrderCancelled(
            id=event_id,
            source=source,
            subject=subject,
            time=now,
            tenant_id=tenant_id,
            data=order,
        )
    elif action == "updated":
        logger.info(
            "Created OrderUpdated event",
            event_id=event_id,
            order_id=order.id,
            tenant_id=tenant_id,
        )
        return OrderUpdated(
            id=event_id,
            source=source,
            subject=subject,
            time=now,
            tenant_id=tenant_id,
            data=order,
        )

    logger.info(
        "Created OrderCreated event",
        event_id=event_id,
        order_id=order.id,
        tenant_id=tenant_id,
    )
    return OrderCreated(
        id=event_id,
        source=source,
        subject=subject,
        time=now,
        tenant_id=tenant_id,
        data=order,
    )


async def fetch_order_details(
    client: WooCommerceClient,
    order_id: int,
) -> Order:
    """Fetch order details from WooCommerce store via REST API."""
    logger.info("Fetching order details from WooCommerce", order_id=order_id)
    raw_order = await client.get_order(order_id)
    order = Order.model_validate(raw_order)
    logger.info(
        "Order details retrieved successfully",
        order_id=order_id,
        status=order.status,
    )
    return order


async def submit_order(client: WooCommerceClient, order: Order) -> dict[str, Any]:
    """Submit or update order in WooCommerce store with clean 1:1 serialization."""
    logger.info("Submitting order to WooCommerce store", order_id=order.id)
    body = order.model_dump(exclude_unset=True, exclude_none=True)

    if order.id:
        result = await client.update_order(order.id, body)
        logger.info("Order updated successfully", order_id=order.id)
    else:
        result = await client.create_order(body)
        logger.info("Order created successfully", order_id=result.get("id"))

    return result


__all__ = [
    "fetch_order_details",
    "parse_order_webhook",
    "submit_order",
]
