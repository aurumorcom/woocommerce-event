"""Windmill script for WordPress/WooCommerce media synchronization."""

import asyncio
import base64
from typing import Any

import structlog
from woocommerce_event.client import WooCommerceEventClient
from woocommerce_event.constants import TOPIC_MEDIA
from woocommerce_event.modules.media.service import (
    parse_media_webhook,
    upload_media,
)
from woocommerce_event.repositories.windmill import (
    WindmillCredentialsRepository,
    WindmillStateRepository,
)

logger = structlog.get_logger(__name__)


async def amain(payload: dict[str, Any]) -> dict[str, Any]:
    """Asynchronous core execution handler."""
    logger.info(
        "Windmill script execution started: media",
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
                "Parsing inbound WooCommerce media webhook",
                tenant_id=tenant_id,
                site_id=site_id,
            )
            event = parse_media_webhook(
                raw_json=payload.get("data", {}),
                tenant_id=tenant_id,
                site_id=site_id,
            )
            publish_res = await client.publish_event(topic=TOPIC_MEDIA, event=event)
            logger.info(
                "Media webhook published to Kafka",
                event_id=event.id,
                status=publish_res.status,
            )
            return {
                "status": "published",
                "event_id": event.id,
                "publish_status": publish_res.status,
            }

        elif action_type == "upload_media":
            filename = payload["filename"]
            content_type = payload.get("content_type", "image/jpeg")
            data_b64 = payload["data_base64"]
            data_bytes = base64.b64decode(data_b64)

            wc_client = await client.get_authenticated_wc_client(
                tenant_id=tenant_id, site_id=site_id
            )
            media_item = await upload_media(
                client=wc_client,
                filename=filename,
                content_type=content_type,
                data=data_bytes,
            )
            logger.info("Outbound media uploaded", media_id=media_item.id)
            return {"status": "success", "media": media_item.model_dump()}

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
