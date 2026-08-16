"""Windmill Resource and State repository implementations."""

import asyncio
import os
from typing import Any

import structlog

from woocommerce_event.exceptions import CredentialsNotFoundError
from woocommerce_event.schemas import Credentials
from woocommerce_event.utils.proquint import (
    get_proquint_windmill_resource_path,
)

logger = structlog.get_logger(__name__)


class WindmillCredentialsRepository:
    """Resolves WooCommerce credentials from Windmill resources or environment variables."""

    def __init__(self, resource_path_prefix: str = "f/woocommerce_event/") -> None:
        self.resource_path_prefix = resource_path_prefix
        logger.debug(
            "Initialized WindmillCredentialsRepository",
            prefix=self.resource_path_prefix,
        )

    async def get_credentials(
        self, tenant_id: int | str, site_id: int | str
    ) -> Credentials:
        """Resolve credentials from Windmill resource path or environment fallback."""
        logger.debug(
            "Resolving credentials in WindmillCredentialsRepository",
            tenant_id=tenant_id,
            site_id=site_id,
        )
        resource_path = get_proquint_windmill_resource_path(tenant_id, site_id)

        # 1. Try resolving via wmill SDK if in Windmill runtime
        try:
            import wmill  # type: ignore[import-untyped]

            res = await asyncio.to_thread(wmill.get_resource, resource_path)
            if res and isinstance(res, dict):
                logger.info(
                    "Credentials retrieved from Windmill resource",
                    resource_path=resource_path,
                    tenant_id=tenant_id,
                    site_id=site_id,
                )
                return Credentials(
                    site_url=res.get("url")
                    or res.get("site_url")
                    or res.get("siteUrl", ""),
                    consumer_key=res.get("consumerKey") or res.get("consumer_key", ""),
                    consumer_secret=res.get("consumerSecret")
                    or res.get("consumer_secret", ""),
                    webhook_secret=res.get("webhookSecret")
                    or res.get("webhook_secret"),
                )
        except Exception as exc:  # noqa: BLE001
            logger.debug(
                "Windmill resource lookup skipped/failed",
                resource_path=resource_path,
                error=str(exc),
            )

        # 2. Fallback to environment variables
        env_site_url = os.environ.get("WOOCOMMERCE_SITE_URL") or os.environ.get(
            "WORDPRESS_SITE_URL"
        )
        env_ck = os.environ.get("WOOCOMMERCE_CONSUMER_KEY")
        env_cs = os.environ.get("WOOCOMMERCE_CONSUMER_SECRET")
        env_whsec = os.environ.get("WOOCOMMERCE_WEBHOOK_SECRET")

        if env_site_url and env_ck and env_cs:
            logger.info(
                "Credentials resolved from environment variables",
                tenant_id=tenant_id,
                site_id=site_id,
            )
            return Credentials(
                site_url=env_site_url,
                consumer_key=env_ck,
                consumer_secret=env_cs,
                webhook_secret=env_whsec,
            )

        logger.error(
            "Failed to resolve credentials from Windmill and environment",
            tenant_id=tenant_id,
            site_id=site_id,
            resource_path=resource_path,
        )
        raise CredentialsNotFoundError(
            f"Credentials not found for tenant '{tenant_id}' and site '{site_id}' in Windmill path '{resource_path}'"
        )


class WindmillStateRepository:
    """Caches execution state via Windmill variables / local cache fallback."""

    def __init__(self, variable_prefix: str = "f/woocommerce_event/state_") -> None:
        self.variable_prefix = variable_prefix
        self._local_cache: dict[str, Any] = {}
        logger.debug("Initialized WindmillStateRepository", prefix=self.variable_prefix)

    async def get_state(self, key: str) -> Any | None:
        """Retrieve state from Windmill variable or local cache."""
        var_path = f"{self.variable_prefix}{key}"
        logger.debug("Querying WindmillStateRepository", key=key, var_path=var_path)

        if key in self._local_cache:
            logger.debug("Cache hit in WindmillStateRepository local cache", key=key)
            return self._local_cache[key]

        try:
            import wmill  # type: ignore[import-untyped]

            val = await asyncio.to_thread(wmill.get_variable, var_path)
            if val is not None:
                self._local_cache[key] = val
                logger.info("State retrieved from Windmill variable", var_path=var_path)
                return val
        except Exception as exc:  # noqa: BLE001
            logger.debug(
                "Windmill variable get skipped/failed",
                var_path=var_path,
                error=str(exc),
            )

        return None

    async def set_state(self, key: str, value: Any, ttl_seconds: int = 3600) -> None:
        """Persist state to Windmill variable and local cache."""
        var_path = f"{self.variable_prefix}{key}"
        self._local_cache[key] = value
        logger.debug(
            "Setting state in WindmillStateRepository",
            key=key,
            var_path=var_path,
        )

        try:
            import wmill  # type: ignore[import-untyped]

            await asyncio.to_thread(wmill.set_variable, var_path, value)
            logger.info(
                "State successfully set in Windmill variable", var_path=var_path
            )
        except Exception as exc:  # noqa: BLE001
            logger.debug(
                "Windmill variable set skipped/failed",
                var_path=var_path,
                error=str(exc),
            )


__all__ = ["WindmillCredentialsRepository", "WindmillStateRepository"]
