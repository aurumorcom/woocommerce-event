"""Windmill script for WooCommerce tags synchronization."""

import asyncio
from typing import Any

import structlog
from woocommerce_event.client import WooCommerceEventClient
from woocommerce_event.constants import TOPIC_ITEM_TAG
from woocommerce_event.modules.tags.schemas import Tag
from woocommerce_event.modules.tags.service import (
    parse_tag_webhook,
    upsert_tag,
)
from woocommerce_event.repositories.windmill import (
    WindmillCredentialsRepository,
    WindmillStateRepository,
)

logger = structlog.get_logger(__name__)


async def amain(payload: dict[str, Any]) -> dict[str, Any]:
    """Asynchronous core execution handler."""
    logger.info(
        "Windmill script execution started: tags",
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
                "Parsing inbound WooCommerce tag webhook",
                tenant_id=tenant_id,
                site_id=site_id,
            )
            event = parse_tag_webhook(
                raw_json=payload.get("data", {}),
                tenant_id=tenant_id,
                site_id=site_id,
            )
            publish_res = await client.publish_event(topic=TOPIC_ITEM_TAG, event=event)
            logger.info(
                "Tag webhook published to Kafka",
                event_id=event.id,
                status=publish_res.status,
            )
            return {
                "status": "published",
                "event_id": event.id,
                "publish_status": publish_res.status,
            }

        elif action_type in ("upsert_tag", "submit_tag"):
            tag = Tag.model_validate(payload["tag"])
            wc_client = await client.get_authenticated_wc_client(
                tenant_id=tenant_id, site_id=site_id
            )
            response = await upsert_tag(client=wc_client, tag=tag)
            logger.info(
                "Outbound tag processed in WooCommerce",
                tag_id=response.get("id"),
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
