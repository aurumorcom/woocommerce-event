"""Windmill script for WooCommerce product attributes synchronization."""

import asyncio
from typing import Any

import structlog
from woocommerce_event.client import WooCommerceEventClient
from woocommerce_event.constants import (
    TOPIC_ITEM_ATTRIBUTE,
    TOPIC_ITEM_ATTRIBUTE_VALUE,
)
from woocommerce_event.modules.attributes.schemas import (
    Attribute,
    AttributeTerm,
)
from woocommerce_event.modules.attributes.service import (
    parse_attribute_term_webhook,
    parse_attribute_webhook,
    upsert_attribute,
    upsert_attribute_term,
)
from woocommerce_event.repositories.windmill import (
    WindmillCredentialsRepository,
    WindmillStateRepository,
)

logger = structlog.get_logger(__name__)


async def amain(payload: dict[str, Any]) -> dict[str, Any]:
    """Asynchronous core execution handler."""
    logger.info(
        "Windmill script execution started: attributes",
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
                "Parsing inbound WooCommerce attribute webhook",
                tenant_id=tenant_id,
                site_id=site_id,
            )
            event = parse_attribute_webhook(
                raw_json=payload.get("data", {}),
                tenant_id=tenant_id,
                site_id=site_id,
            )
            publish_res = await client.publish_event(
                topic=TOPIC_ITEM_ATTRIBUTE, event=event
            )
            logger.info(
                "Attribute webhook published to Kafka",
                event_id=event.id,
                status=publish_res.status,
            )
            return {
                "status": "published",
                "event_id": event.id,
                "publish_status": publish_res.status,
            }

        elif action_type == "webhook_term":
            attribute_id = int(payload.get("attribute_id", 0))
            event_term = parse_attribute_term_webhook(
                raw_json=payload.get("data", {}),
                attribute_id=attribute_id,
                tenant_id=tenant_id,
                site_id=site_id,
            )
            publish_res = await client.publish_event(
                topic=TOPIC_ITEM_ATTRIBUTE_VALUE, event=event_term
            )
            return {
                "status": "published",
                "event_id": event_term.id,
                "publish_status": publish_res.status,
            }

        elif action_type in ("upsert_attribute", "submit_attribute"):
            attr = Attribute.model_validate(payload["attribute"])
            wc_client = await client.get_authenticated_wc_client(
                tenant_id=tenant_id, site_id=site_id
            )
            response = await upsert_attribute(client=wc_client, attr=attr)
            logger.info(
                "Outbound attribute processed in WooCommerce",
                attribute_id=response.get("id"),
            )
            return {"status": "success", "data": response}

        elif action_type in ("upsert_term", "submit_term"):
            attribute_id = int(payload["attribute_id"])
            term = AttributeTerm.model_validate(payload["term"])
            wc_client = await client.get_authenticated_wc_client(
                tenant_id=tenant_id, site_id=site_id
            )
            response = await upsert_attribute_term(
                client=wc_client, attribute_id=attribute_id, term=term
            )
            logger.info(
                "Outbound term processed in WooCommerce",
                term_id=response.get("id"),
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
