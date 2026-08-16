"""Windmill script for WooCommerce orders synchronization."""

import asyncio
from typing import Any

import structlog
from woocommerce_event.client import WooCommerceEventClient
from woocommerce_event.constants import TOPIC_SALES_ORDER
from woocommerce_event.modules.orders.schemas import Order
from woocommerce_event.modules.orders.service import (
    fetch_order_details,
    parse_order_webhook,
    submit_order,
)
from woocommerce_event.repositories.windmill import (
    WindmillCredentialsRepository,
    WindmillStateRepository,
)

logger = structlog.get_logger(__name__)


async def amain(payload: dict[str, Any]) -> dict[str, Any]:
    """Asynchronous core execution handler."""
    logger.info(
        "Windmill script execution started: orders",
        payload_keys=list(payload.keys()),
    )

    async with WooCommerceEventClient(
        credentials_repo=WindmillCredentialsRepository(),
        state_repo=WindmillStateRepository(),
    ) as client:
        action_type = payload.get("action_type", "webhook")
        tenant_id = payload.get("tenant_id", 1)
        site_id = payload.get(
            "subject", payload.get("site_id", payload.get("channel_id", 1))
        )

        if action_type == "webhook":
            logger.debug(
                "Parsing inbound WooCommerce order webhook",
                tenant_id=tenant_id,
                site_id=site_id,
            )
            event = parse_order_webhook(
                raw_json=payload.get("data", {}),
                tenant_id=tenant_id,
                site_id=site_id,
            )
            publish_res = await client.publish_event(
                topic=TOPIC_SALES_ORDER, event=event
            )
            logger.info(
                "Order webhook published to Kafka",
                event_id=event.id,
                status=publish_res.status,
            )
            return {
                "status": "published",
                "event_id": event.id,
                "publish_status": publish_res.status,
            }

        elif action_type == "fetch_order":
            order_id = int(payload["order_id"])
            wc_client = await client.get_authenticated_wc_client(
                tenant_id=tenant_id, site_id=site_id
            )
            order = await fetch_order_details(
                client=wc_client,
                order_id=order_id,
            )
            logger.info("Order fetched successfully", order_id=order.id)
            return {"status": "success", "order": order.model_dump()}

        elif action_type == "submit_order":
            order = Order.model_validate(payload["order"])
            wc_client = await client.get_authenticated_wc_client(
                tenant_id=tenant_id, site_id=site_id
            )
            response = await submit_order(client=wc_client, order=order)
            logger.info("Order submitted successfully", order_id=response.get("id"))
            return {"status": "success", "data": response}

        logger.warning(
            "Unrecognized action_type in Windmill script payload",
            action_type=action_type,
        )
        return {
            "status": "ignored",
            "reason": f"unrecognized action_type: {action_type}",
        }


def main(payload: dict[str, Any]) -> dict[str, Any]:
    """Synchronous Windmill entrypoint executing the asynchronous engine."""
    return asyncio.run(amain(payload))
