"""Windmill script for WooCommerce multi-tenant site provisioning."""

import asyncio
from datetime import UTC, datetime
from typing import Any

import structlog
from woocommerce_event.client import WooCommerceEventClient
from woocommerce_event.constants import TOPIC_CHANNEL
from woocommerce_event.modules.sites.schemas import ChannelCreated
from woocommerce_event.modules.sites.service import register_site_topology
from woocommerce_event.repositories.windmill import (
    WindmillCredentialsRepository,
    WindmillStateRepository,
)
from woocommerce_event.schemas import Site

logger = structlog.get_logger(__name__)


async def amain(payload: dict[str, Any]) -> dict[str, Any]:
    """Asynchronous core execution handler."""
    logger.info(
        "Windmill script execution started: sites",
        payload_keys=list(payload.keys()),
    )

    async with WooCommerceEventClient(
        credentials_repo=WindmillCredentialsRepository(),
        state_repo=WindmillStateRepository(),
    ) as client:
        action_type = payload.get("action_type", "provision")
        tenant_id = payload.get("tenant_id", 1)
        site_id = payload.get(
            "subject", payload.get("site_id", payload.get("channel_id", 1))
        )
        environment = payload.get("environment", "production")

        site_context = Site(
            tenant_id=tenant_id,
            site_id=site_id,
            environment=environment,
        )

        if action_type == "provision":
            await register_site_topology(client=client, site_context=site_context)
            event = ChannelCreated(
                id=f"site-prov-{tenant_id}-{site_id}",
                source=f"woocommerce://{site_id}/sites",
                subject=str(site_id),
                time=datetime.now(UTC),
                tenant_id=tenant_id,
                data=site_context,
            )
            publish_res = await client.publish_event(topic=TOPIC_CHANNEL, event=event)
            logger.info(
                "Site provisioned and announced to Kafka",
                status=publish_res.status,
            )
            return {
                "status": "provisioned",
                "tenant_id": tenant_id,
                "site_id": site_id,
                "publish_status": publish_res.status,
            }

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
