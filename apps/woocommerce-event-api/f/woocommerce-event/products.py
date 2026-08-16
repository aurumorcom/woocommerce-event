"""Windmill script for WooCommerce products synchronization."""

import asyncio
from typing import Any

import structlog
from woocommerce_event.client import WooCommerceEventClient
from woocommerce_event.constants import TOPIC_PRODUCT
from woocommerce_event.modules.products.schemas import Product
from woocommerce_event.modules.products.service import (
    parse_product_webhook,
    upsert_product,
)
from woocommerce_event.repositories.windmill import (
    WindmillCredentialsRepository,
    WindmillStateRepository,
)

logger = structlog.get_logger(__name__)


async def amain(payload: dict[str, Any]) -> dict[str, Any]:
    """Asynchronous core execution handler."""
    logger.info(
        "Windmill script execution started: products",
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
                "Parsing inbound WooCommerce product webhook",
                tenant_id=tenant_id,
                site_id=site_id,
            )
            event = parse_product_webhook(
                raw_json=payload.get("data", {}),
                tenant_id=tenant_id,
                site_id=site_id,
            )
            publish_res = await client.publish_event(topic=TOPIC_PRODUCT, event=event)
            logger.info(
                "Product webhook published to Kafka",
                event_id=event.id,
                status=publish_res.status,
            )
            return {
                "status": "published",
                "event_id": event.id,
                "publish_status": publish_res.status,
            }

        elif action_type in ("upsert_product", "submit_product"):
            logger.debug("Validating outbound product payload")
            product = Product.model_validate(payload["product"])
            wc_client = await client.get_authenticated_wc_client(
                tenant_id=tenant_id, site_id=site_id
            )
            response = await upsert_product(client=wc_client, product=product)
            logger.info(
                "Outbound product processed in WooCommerce",
                wc_product_id=response.get("id"),
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
