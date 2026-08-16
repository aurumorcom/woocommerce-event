"""Site/Channel provisioning service execution logic."""

from typing import Any

import structlog

from woocommerce_event.constants import TOPIC_CHANNEL
from woocommerce_event.modules.sites.schemas import ChannelCreated
from woocommerce_event.schemas import Site

logger = structlog.get_logger(__name__)


async def register_site_topology(client: Any, site_context: Site) -> None:
    """Provision streaming topology and topics on RisingWave/Kafka for WooCommerce site."""
    logger.info(
        "Provisioning streaming topology for WooCommerce site",
        tenant_id=site_context.tenant_id,
        site_id=site_context.site_id,
    )
    if hasattr(client, "event_client") and hasattr(
        client.event_client, "aprovision_topology"
    ):
        await client.event_client.aprovision_topology(
            event_cls=ChannelCreated,
            topic=TOPIC_CHANNEL,
        )
    logger.info(
        "Site streaming topology provisioned successfully",
        tenant_id=site_context.tenant_id,
        site_id=site_context.site_id,
    )


__all__ = ["register_site_topology"]
