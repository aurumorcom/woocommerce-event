"""In-memory fake repositories for testing and isolated local environments."""

import time
from typing import Any

import structlog

from woocommerce_event.exceptions import CredentialsNotFoundError
from woocommerce_event.schemas import Credentials

logger = structlog.get_logger(__name__)


class MemoryCredentialsRepository:
    """In-memory credentials repository implementation."""

    def __init__(
        self,
        initial_credentials: dict[tuple[str, str], Credentials] | None = None,
    ) -> None:
        self._store: dict[tuple[str, str], Credentials] = initial_credentials or {}
        logger.debug(
            "Initialized MemoryCredentialsRepository",
            initial_count=len(self._store),
        )

    def add_credentials(
        self, tenant_id: int | str, site_id: int | str, credentials: Credentials
    ) -> None:
        """Helper to register credentials for a specific tenant and site."""
        self._store[(str(tenant_id), str(site_id))] = credentials
        logger.info(
            "Added credentials to MemoryCredentialsRepository",
            tenant_id=tenant_id,
            site_id=site_id,
        )

    async def get_credentials(
        self, tenant_id: int | str, site_id: int | str
    ) -> Credentials:
        """Resolve credentials from in-memory dictionary."""
        logger.debug(
            "Querying MemoryCredentialsRepository",
            tenant_id=tenant_id,
            site_id=site_id,
        )
        creds = self._store.get((str(tenant_id), str(site_id)))
        if not creds:
            logger.error(
                "Credentials not found in memory store",
                tenant_id=tenant_id,
                site_id=site_id,
            )
            raise CredentialsNotFoundError(
                f"Credentials not found for tenant '{tenant_id}' and site '{site_id}'"
            )
        logger.info(
            "Credentials resolved from MemoryCredentialsRepository",
            tenant_id=tenant_id,
            site_id=site_id,
        )
        return creds


class MemoryStateRepository:
    """In-memory state cache repository with TTL support."""

    def __init__(self) -> None:
        self._store: dict[str, tuple[Any, float]] = {}
        logger.debug("Initialized MemoryStateRepository")

    async def get_state(self, key: str) -> Any | None:
        """Retrieve state from cache if not expired."""
        logger.debug("Querying MemoryStateRepository", key=key)
        entry = self._store.get(key)
        if entry is None:
            logger.debug("Cache miss in MemoryStateRepository", key=key)
            return None

        val, expiry = entry
        if time.time() > expiry:
            logger.debug("Cache entry expired in MemoryStateRepository", key=key)
            del self._store[key]
            return None

        logger.debug("Cache hit in MemoryStateRepository", key=key)
        return val

    async def set_state(self, key: str, value: Any, ttl_seconds: int = 3600) -> None:
        """Persist state to cache with TTL."""
        expiry = time.time() + ttl_seconds
        self._store[key] = (value, expiry)
        logger.debug(
            "Set cache value in MemoryStateRepository",
            key=key,
            ttl_seconds=ttl_seconds,
        )


__all__ = ["MemoryCredentialsRepository", "MemoryStateRepository"]
