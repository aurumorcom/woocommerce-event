"""Windmill script for WooCommerce categories synchronization."""

import asyncio
from typing import Any

import structlog
from woocommerce_event.client import WooCommerceEventClient
from woocommerce_event.constants import TOPIC_ITEM_CATEGORY
from woocommerce_event.modules.categories.schemas import Category
from woocommerce_event.modules.categories.service import (
    parse_category_webhook,
    upsert_category,
)
from woocommerce_event.repositories.windmill import (
    WindmillCredentialsRepository,
    WindmillStateRepository,
)

logger = structlog.get_logger(__name__)


async def amain(payload: dict[str, Any]) -> dict[str, Any]:
    """Asynchronous core execution handler."""
    logger.info(
        "Windmill script execution started: categories",
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
                "Parsing inbound WooCommerce category webhook",
                tenant_id=tenant_id,
                site_id=site_id,
            )
            event = parse_category_webhook(
                raw_json=payload.get("data", {}),
                tenant_id=tenant_id,
                site_id=site_id,
            )
            publish_res = await client.publish_event(
                topic=TOPIC_ITEM_CATEGORY, event=event
            )
            logger.info(
                "Category webhook published to Kafka",
                event_id=event.id,
                status=publish_res.status,
            )
            return {
                "status": "published",
                "event_id": event.id,
                "publish_status": publish_res.status,
            }

        elif action_type in ("upsert_category", "submit_category"):
            category = Category.model_validate(payload["category"])
            wc_client = await client.get_authenticated_wc_client(
                tenant_id=tenant_id, site_id=site_id
            )
            response = await upsert_category(client=wc_client, category=category)
            logger.info(
                "Outbound category processed in WooCommerce",
                category_id=response.get("id"),
            )
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
