"""Async Facade Client (WooCommerceEventClient) wrapping EventClient, WooCommerceClient, and Repositories."""

import types
from typing import Any, Self

import structlog
from python_event.client import EventClient, PublishResponse
from python_event.modules.events.schemas import EventBaseModel

from woocommerce_event.constants import TOPICS
from woocommerce_event.exceptions import WooCommercePublishError
from woocommerce_event.integrations.woocommerce import (
    WooCommerceClient,
)
from woocommerce_event.protocols import CredentialsRepository, StateRepository
from woocommerce_event.repositories.memory import (
    MemoryCredentialsRepository,
    MemoryStateRepository,
)
from woocommerce_event.schemas import Credentials

logger = structlog.get_logger(__name__)


class WooCommerceEventClient:
    """Async Stateful Client Facade coordinating event publishing, credentials resolution, and WooCommerce API calls."""

    def __init__(
        self,
        event_client: EventClient | None = None,
        credentials_repo: CredentialsRepository | None = None,
        state_repo: StateRepository | None = None,
    ) -> None:
        self.event_client = event_client or EventClient()
        self.credentials_repo = credentials_repo or MemoryCredentialsRepository()
        self.state_repo = state_repo or MemoryStateRepository()
        self._active_api_clients: list[WooCommerceClient] = []
        logger.debug("Initialized WooCommerceEventClient facade")

    async def publish_event(
        self,
        topic: str,
        event: EventBaseModel,
        schema_id: int | None = None,
        key: str | int | None = None,
        headers: dict[str, Any] | None = None,
    ) -> PublishResponse:
        """Publish a CloudEvent to a Kafka topic asynchronously."""
        if topic not in TOPICS:
            error_msg = (
                f"Invalid topic '{topic}'. Must be one of the canonical topics: "
                f"{sorted(TOPICS)}"
            )
            logger.error("Attempted to publish to non-canonical topic", topic=topic)
            raise ValueError(error_msg)

        partition_key = key
        if partition_key is None and hasattr(event, "tenant_id"):
            partition_key = event.tenant_id
        if (
            partition_key is None
            and hasattr(event, "data")
            and hasattr(event.data, "tenant_id")
        ):
            partition_key = event.data.tenant_id
        if partition_key is None:
            partition_key = getattr(event, "subject", "default")

        str_key = str(partition_key)

        logger.debug(
            "Publishing event to Kafka topic",
            topic=topic,
            event_type=event.type,
            partition_key=str_key,
        )

        try:
            publish_res = await self.event_client.apublish_event(
                topic=topic,
                event=event,
                schema_id=schema_id,
                key=str_key,
                headers=headers,
            )
            logger.info(
                "Successfully published event to Kafka topic",
                topic=topic,
                event_type=event.type,
                partition_key=str_key,
            )
            return publish_res
        except Exception as exc:
            logger.exception(
                "Failed to publish event to Kafka",
                topic=topic,
                event_type=event.type,
                error=str(exc),
            )
            raise WooCommercePublishError(f"Failed to publish event: {exc}") from exc

    async def get_authenticated_wc_client(
        self, tenant_id: int | str, site_id: int | str = "default_site"
    ) -> WooCommerceClient:
        """Resolve tenant credentials and return an authenticated WooCommerce REST API client."""
        logger.debug(
            "Resolving authenticated WooCommerce client",
            tenant_id=tenant_id,
            site_id=site_id,
        )
        cache_key = f"credentials:{tenant_id}:{site_id}"

        cached_entry = await self.state_repo.get_state(cache_key)
        if cached_entry is not None:
            logger.info("Credentials cache hit", tenant_id=tenant_id, site_id=site_id)
            if isinstance(cached_entry, dict):
                creds = Credentials.model_validate(cached_entry)
            elif isinstance(cached_entry, Credentials):
                creds = cached_entry
            else:
                creds = Credentials.model_validate(cached_entry)
        else:
            logger.warning(
                "Credentials cache miss, querying CredentialsRepository",
                tenant_id=tenant_id,
                site_id=site_id,
            )
            creds = await self.credentials_repo.get_credentials(tenant_id, site_id)
            await self.state_repo.set_state(
                cache_key, creds.model_dump(), ttl_seconds=3600
            )
            logger.info(
                "Successfully resolved and cached credentials",
                tenant_id=tenant_id,
                site_id=site_id,
            )

        client = WooCommerceClient(
            site_url=creds.site_url,
            consumer_key=creds.consumer_key,
            consumer_secret=creds.consumer_secret,
        )
        self._active_api_clients.append(client)
        return client

    async def aclose(self) -> None:
        """Close event client and all active WooCommerce HTTP clients."""
        logger.debug("Closing WooCommerceEventClient and underlying event client")
        for client in self._active_api_clients:
            await client.aclose()
        self._active_api_clients.clear()
        await self.event_client.aclose()
        logger.info("WooCommerceEventClient closed successfully")

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: types.TracebackType | None,
    ) -> None:
        await self.aclose()


__all__ = ["WooCommerceEventClient"]
