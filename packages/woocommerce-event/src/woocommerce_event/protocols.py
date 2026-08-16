"""Asynchronous protocols for credentials and state caching."""

from typing import Any, Protocol, runtime_checkable

from woocommerce_event.schemas import Credentials


@runtime_checkable
class CredentialsRepository(Protocol):
    """Async protocol for resolving tenant- and site-specific WooCommerce credentials."""

    async def get_credentials(
        self, tenant_id: int | str, site_id: int | str
    ) -> Credentials:
        """Resolve WooCommerce credentials for a specific tenant and site."""
        ...


@runtime_checkable
class StateRepository(Protocol):
    """Async protocol for cross-invocation state caching (e.g. webhook delivery nonces, tokens)."""

    async def get_state(self, key: str) -> Any | None:
        """Retrieve state from cache."""
        ...

    async def set_state(self, key: str, value: Any, ttl_seconds: int = 3600) -> None:
        """Persist state to cache with time-to-live."""
        ...


__all__ = ["CredentialsRepository", "StateRepository"]
