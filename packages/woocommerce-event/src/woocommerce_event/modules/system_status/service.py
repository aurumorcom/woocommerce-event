"""System status domain service execution logic."""

import structlog

from woocommerce_event.integrations.woocommerce import WooCommerceClient
from woocommerce_event.modules.system_status.schemas import (
    DatabaseInfo,
    EnvironmentInfo,
    SecurityInfo,
    SystemStatus,
)

logger = structlog.get_logger(__name__)


async def fetch_system_health(
    client: WooCommerceClient,
) -> SystemStatus:
    """Query WooCommerce system status and environment summary."""
    logger.info("Querying WooCommerce system status and environment health")
    raw_status = await client.get_system_status()

    env_dict = raw_status.get("environment") or {}
    db_dict = raw_status.get("database") or {}
    sec_dict = raw_status.get("security") or {}

    status = SystemStatus(
        environment=EnvironmentInfo(
            home_url=env_dict.get("home_url"),
            site_url=env_dict.get("site_url"),
            version=env_dict.get("version"),
            wp_version=env_dict.get("wp_version"),
            php_version=env_dict.get("php_version"),
            server_info=env_dict.get("server_info"),
        ),
        database=DatabaseInfo(
            wc_database_version=db_dict.get("wc_database_version"),
            database_prefix=db_dict.get("database_prefix"),
            maxmind_geoip_database=db_dict.get("maxmind_geoip_database"),
        ),
        security=SecurityInfo(
            secure_connection=sec_dict.get("secure_connection", True),
            hide_errors=sec_dict.get("hide_errors", True),
        ),
        settings=raw_status.get("settings") or {},
    )
    logger.info(
        "System status retrieved successfully",
        wp_version=status.environment.wp_version if status.environment else None,
    )
    return status


__all__ = ["fetch_system_health"]
