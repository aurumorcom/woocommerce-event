"""Windmill script for WooCommerce system status sampling."""

import asyncio
from datetime import UTC, datetime
from typing import Any

import structlog
from woocommerce_event.client import WooCommerceEventClient
from woocommerce_event.constants import TOPIC_CHANNEL
from woocommerce_event.modules.system_status.schemas import SystemStatusSampled
from woocommerce_event.modules.system_status.service import fetch_system_health
from woocommerce_event.repositories.windmill import (
    WindmillCredentialsRepository,
    WindmillStateRepository,
)

logger = structlog.get_logger(__name__)


async def amain(payload: dict[str, Any]) -> dict[str, Any]:
    """Asynchronous core execution handler."""
    logger.info(
        "Windmill script execution started: system_status",
        payload_keys=list(payload.keys()),
    )

    async with WooCommerceEventClient(
        credentials_repo=WindmillCredentialsRepository(),
        state_repo=WindmillStateRepository(),
    ) as client:
        tenant_id = payload.get("tenant_id", 1)
        site_id = payload.get(
            "subject", payload.get("site_id", payload.get("channel_id", 1))
        )

        wc_client = await client.get_authenticated_wc_client(
            tenant_id=tenant_id, site_id=site_id
        )
        status = await fetch_system_health(client=wc_client)

        # Publish system status snapshot event
        event = SystemStatusSampled(
            id=f"health-{tenant_id}-{site_id}",
            source=f"woocommerce://{site_id}/system_status",
            subject=str(site_id),
            time=datetime.now(UTC),
            tenant_id=tenant_id,
            data=status,
        )
        publish_res = await client.publish_event(topic=TOPIC_CHANNEL, event=event)
        logger.info("System status sampled and published", status=publish_res.status)
        return {
            "status": "success",
            "system_status": status.model_dump(),
            "publish_status": publish_res.status,
        }


def main(payload: dict[str, Any]) -> dict[str, Any]:
    """Synchronous Windmill entrypoint executing the asynchronous engine."""
    return asyncio.run(amain(payload))
