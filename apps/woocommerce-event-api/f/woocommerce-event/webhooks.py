"""Windmill script for WooCommerce webhook provisioning and ingress validation."""

import asyncio
from typing import Any

import structlog
from woocommerce_event.client import WooCommerceEventClient
from woocommerce_event.constants import TOPIC_CHANNEL
from woocommerce_event.modules.webhooks.service import (
    parse_webhook_payload,
    provision_webhooks,
    validate_webhook_hmac_signature,
)
from woocommerce_event.repositories.windmill import (
    WindmillCredentialsRepository,
    WindmillStateRepository,
)

logger = structlog.get_logger(__name__)


async def amain(payload: dict[str, Any]) -> dict[str, Any]:
    """Asynchronous core execution handler."""
    logger.info(
        "Windmill script execution started: webhooks",
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
                "Parsing inbound WooCommerce webhook event",
                tenant_id=tenant_id,
                site_id=site_id,
            )
            event = parse_webhook_payload(
                raw_json=payload.get("data", {}),
                tenant_id=tenant_id,
                site_id=site_id,
            )
            publish_res = await client.publish_event(topic=TOPIC_CHANNEL, event=event)
            logger.info(
                "Webhook metadata published to Kafka",
                event_id=event.id,
                status=publish_res.status,
            )
            return {
                "status": "published",
                "event_id": event.id,
                "publish_status": publish_res.status,
            }

        elif action_type == "verify_signature":
            raw_body = (
                payload["raw_body"].encode("utf-8")
                if isinstance(payload["raw_body"], str)
                else payload["raw_body"]
            )
            sig = payload["signature"]
            secret = payload["secret"]
            is_valid = validate_webhook_hmac_signature(
                raw_payload=raw_body, signature_header=sig, secret=secret
            )
            return {"valid": is_valid}

        elif action_type == "provision":
            delivery_url = payload["delivery_url"]
            secret = payload["secret"]
            topics = payload.get("topics")
            wc_client = await client.get_authenticated_wc_client(
                tenant_id=tenant_id, site_id=site_id
            )
            results = await provision_webhooks(
                client=wc_client,
                delivery_url=delivery_url,
                secret=secret,
                topics=topics,
            )
            logger.info("Webhooks provisioned in WooCommerce", count=len(results))
            return {"status": "success", "webhooks": results}

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
