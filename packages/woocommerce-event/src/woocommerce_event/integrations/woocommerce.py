"""Stateful Async WooCommerce REST API Client with 1:1 endpoint method names and 100% structured logging."""

import logging
import types
from typing import Any, Self

import httpx
import structlog
from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from woocommerce_event.exceptions import (
    WooCommerceAPIError,
    WooCommerceAuthenticationError,
    WooCommerceRateLimitError,
)

logger = structlog.get_logger(__name__)


class WooCommerceClient:
    """Stateful Async WooCommerce REST API Client with 1:1 endpoint method names and 100% structured logging."""

    def __init__(
        self,
        site_url: str,
        consumer_key: str,
        consumer_secret: str,
        client: httpx.AsyncClient | None = None,
        timeout: float = 30.0,
    ) -> None:
        self.site_url = site_url.rstrip("/")
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.client = client or httpx.AsyncClient(timeout=timeout)
        logger.debug("Initialized WooCommerceClient", site_url=self.site_url)

    @property
    def auth_headers(self) -> dict[str, str]:
        return {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    async def aclose(self) -> None:
        """Asynchronously close the underlying HTTP client."""
        logger.debug("Closing WooCommerceClient HTTP transport pool")
        await self.client.aclose()
        logger.info("WooCommerceClient HTTP transport closed")

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: types.TracebackType | None,
    ) -> None:
        await self.aclose()

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=1, max=16),
        retry=retry_if_exception_type(WooCommerceRateLimitError),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )
    async def request(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
        files: dict[str, Any] | None = None,
    ) -> dict[str, Any] | list[dict[str, Any]]:
        url = f"{self.site_url}/{path.lstrip('/')}"
        auth = (self.consumer_key, self.consumer_secret)

        headers = self.auth_headers if files is None else {"Accept": "application/json"}
        logger.debug(
            "Executing WooCommerce REST API HTTP request",
            method=method,
            path=path,
            params=params,
        )

        try:
            response = await self.client.request(
                method=method,
                url=url,
                auth=auth,
                headers=headers,
                params=params,
                json=json_body,
                files=files,
            )
        except httpx.RequestError as exc:
            logger.exception(
                "HTTP transport failure during WooCommerce request",
                method=method,
                url=url,
                error=str(exc),
            )
            raise WooCommerceAPIError(f"HTTP transport failure: {exc}") from exc

        if response.status_code == 429:
            logger.warning(
                "WooCommerce REST API rate limit reached (429)",
                path=path,
                method=method,
                retry_after=response.headers.get("Retry-After"),
            )
            raise WooCommerceRateLimitError("WooCommerce REST API rate limit exceeded")
        if response.status_code in (401, 403):
            logger.error(
                "WooCommerce authentication failed",
                status_code=response.status_code,
                path=path,
            )
            raise WooCommerceAuthenticationError(
                f"Authentication failed ({response.status_code}): {response.text}"
            )
        if response.is_error:
            logger.error(
                "WooCommerce API returned HTTP error response",
                status_code=response.status_code,
                path=path,
                method=method,
                response_body=response.text,
            )
            raise WooCommerceAPIError(
                f"WooCommerce API error {response.status_code}: {response.text}"
            )

        logger.info(
            "WooCommerce request completed successfully",
            method=method,
            path=path,
            status_code=response.status_code,
        )
        return response.json()

    # 1. Products API (wc/v3/products)
    async def get_product(self, product_id: int) -> dict[str, Any]:
        """Fetch a single product by ID."""
        logger.debug("Calling get_product", product_id=product_id)
        result = await self.request("GET", f"/wp-json/wc/v3/products/{product_id}")
        return result  # type: ignore[return-value]

    async def list_products(
        self, params: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """List products with optional pagination and filtering."""
        logger.debug("Calling list_products", params=params)
        result = await self.request("GET", "/wp-json/wc/v3/products", params=params)
        return result  # type: ignore[return-value]

    async def create_product(self, body: dict[str, Any]) -> dict[str, Any]:
        """Create a new product."""
        logger.debug(
            "Calling create_product",
            sku=body.get("sku"),
            name=body.get("name"),
        )
        result = await self.request("POST", "/wp-json/wc/v3/products", json_body=body)
        return result  # type: ignore[return-value]

    async def update_product(
        self, product_id: int, body: dict[str, Any]
    ) -> dict[str, Any]:
        """Update an existing product."""
        logger.debug("Calling update_product", product_id=product_id)
        result = await self.request(
            "PUT", f"/wp-json/wc/v3/products/{product_id}", json_body=body
        )
        return result  # type: ignore[return-value]

    async def delete_product(
        self, product_id: int, force: bool = False
    ) -> dict[str, Any]:
        """Delete a product."""
        logger.debug("Calling delete_product", product_id=product_id, force=force)
        params = {"force": "true"} if force else None
        result = await self.request(
            "DELETE", f"/wp-json/wc/v3/products/{product_id}", params=params
        )
        return result  # type: ignore[return-value]

    async def batch_products(self, body: dict[str, Any]) -> dict[str, Any]:
        """Batch create, update, and delete products."""
        logger.debug("Calling batch_products")
        result = await self.request(
            "POST", "/wp-json/wc/v3/products/batch", json_body=body
        )
        return result  # type: ignore[return-value]

    # 2. Product Variations API (wc/v3/products/<id>/variations)
    async def get_variation(self, product_id: int, variation_id: int) -> dict[str, Any]:
        """Fetch a single variation for a product."""
        logger.debug(
            "Calling get_variation",
            product_id=product_id,
            variation_id=variation_id,
        )
        result = await self.request(
            "GET",
            f"/wp-json/wc/v3/products/{product_id}/variations/{variation_id}",
        )
        return result  # type: ignore[return-value]

    async def list_variations(
        self, product_id: int, params: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """List all variations for a product."""
        logger.debug("Calling list_variations", product_id=product_id, params=params)
        result = await self.request(
            "GET", f"/wp-json/wc/v3/products/{product_id}/variations", params=params
        )
        return result  # type: ignore[return-value]

    async def create_variation(
        self, product_id: int, body: dict[str, Any]
    ) -> dict[str, Any]:
        """Create a product variation."""
        logger.debug(
            "Calling create_variation",
            product_id=product_id,
            sku=body.get("sku"),
        )
        result = await self.request(
            "POST",
            f"/wp-json/wc/v3/products/{product_id}/variations",
            json_body=body,
        )
        return result  # type: ignore[return-value]

    async def update_variation(
        self, product_id: int, variation_id: int, body: dict[str, Any]
    ) -> dict[str, Any]:
        """Update a product variation."""
        logger.debug(
            "Calling update_variation",
            product_id=product_id,
            variation_id=variation_id,
        )
        result = await self.request(
            "PUT",
            f"/wp-json/wc/v3/products/{product_id}/variations/{variation_id}",
            json_body=body,
        )
        return result  # type: ignore[return-value]

    async def delete_variation(
        self, product_id: int, variation_id: int, force: bool = False
    ) -> dict[str, Any]:
        """Delete a product variation."""
        logger.debug(
            "Calling delete_variation",
            product_id=product_id,
            variation_id=variation_id,
            force=force,
        )
        params = {"force": "true"} if force else None
        result = await self.request(
            "DELETE",
            f"/wp-json/wc/v3/products/{product_id}/variations/{variation_id}",
            params=params,
        )
        return result  # type: ignore[return-value]

    async def batch_variations(
        self, product_id: int, body: dict[str, Any]
    ) -> dict[str, Any]:
        """Batch create, update, and delete product variations."""
        logger.debug("Calling batch_variations", product_id=product_id)
        result = await self.request(
            "POST",
            f"/wp-json/wc/v3/products/{product_id}/variations/batch",
            json_body=body,
        )
        return result  # type: ignore[return-value]

    # 3. Orders API (wc/v3/orders)
    async def get_order(self, order_id: int) -> dict[str, Any]:
        """Fetch a single order by ID."""
        logger.debug("Calling get_order", order_id=order_id)
        result = await self.request("GET", f"/wp-json/wc/v3/orders/{order_id}")
        return result  # type: ignore[return-value]

    async def list_orders(
        self, params: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """List orders with filtering and pagination."""
        logger.debug("Calling list_orders", params=params)
        result = await self.request("GET", "/wp-json/wc/v3/orders", params=params)
        return result  # type: ignore[return-value]

    async def create_order(self, body: dict[str, Any]) -> dict[str, Any]:
        """Create a new order."""
        logger.debug("Calling create_order")
        result = await self.request("POST", "/wp-json/wc/v3/orders", json_body=body)
        return result  # type: ignore[return-value]

    async def update_order(self, order_id: int, body: dict[str, Any]) -> dict[str, Any]:
        """Update an existing order."""
        logger.debug("Calling update_order", order_id=order_id)
        result = await self.request(
            "PUT", f"/wp-json/wc/v3/orders/{order_id}", json_body=body
        )
        return result  # type: ignore[return-value]

    async def delete_order(self, order_id: int, force: bool = False) -> dict[str, Any]:
        """Delete an order."""
        logger.debug("Calling delete_order", order_id=order_id, force=force)
        params = {"force": "true"} if force else None
        result = await self.request(
            "DELETE", f"/wp-json/wc/v3/orders/{order_id}", params=params
        )
        return result  # type: ignore[return-value]

    # 4. Categories API (wc/v3/products/categories)
    async def get_category(self, category_id: int) -> dict[str, Any]:
        """Fetch a single product category."""
        logger.debug("Calling get_category", category_id=category_id)
        result = await self.request(
            "GET", f"/wp-json/wc/v3/products/categories/{category_id}"
        )
        return result  # type: ignore[return-value]

    async def list_categories(
        self, params: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """List product categories."""
        logger.debug("Calling list_categories", params=params)
        result = await self.request(
            "GET", "/wp-json/wc/v3/products/categories", params=params
        )
        return result  # type: ignore[return-value]

    async def create_category(self, body: dict[str, Any]) -> dict[str, Any]:
        """Create a product category."""
        logger.debug("Calling create_category", name=body.get("name"))
        result = await self.request(
            "POST", "/wp-json/wc/v3/products/categories", json_body=body
        )
        return result  # type: ignore[return-value]

    async def update_category(
        self, category_id: int, body: dict[str, Any]
    ) -> dict[str, Any]:
        """Update a product category."""
        logger.debug("Calling update_category", category_id=category_id)
        result = await self.request(
            "PUT",
            f"/wp-json/wc/v3/products/categories/{category_id}",
            json_body=body,
        )
        return result  # type: ignore[return-value]

    async def delete_category(
        self, category_id: int, force: bool = True
    ) -> dict[str, Any]:
        """Delete a product category."""
        logger.debug("Calling delete_category", category_id=category_id, force=force)
        params = {"force": "true"} if force else None
        result = await self.request(
            "DELETE",
            f"/wp-json/wc/v3/products/categories/{category_id}",
            params=params,
        )
        return result  # type: ignore[return-value]

    # 5. Tags API (wc/v3/products/tags)
    async def get_tag(self, tag_id: int) -> dict[str, Any]:
        """Fetch a single product tag."""
        logger.debug("Calling get_tag", tag_id=tag_id)
        result = await self.request("GET", f"/wp-json/wc/v3/products/tags/{tag_id}")
        return result  # type: ignore[return-value]

    async def list_tags(
        self, params: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """List product tags."""
        logger.debug("Calling list_tags", params=params)
        result = await self.request(
            "GET", "/wp-json/wc/v3/products/tags", params=params
        )
        return result  # type: ignore[return-value]

    async def create_tag(self, body: dict[str, Any]) -> dict[str, Any]:
        """Create a product tag."""
        logger.debug("Calling create_tag", name=body.get("name"))
        result = await self.request(
            "POST", "/wp-json/wc/v3/products/tags", json_body=body
        )
        return result  # type: ignore[return-value]

    async def update_tag(self, tag_id: int, body: dict[str, Any]) -> dict[str, Any]:
        """Update a product tag."""
        logger.debug("Calling update_tag", tag_id=tag_id)
        result = await self.request(
            "PUT", f"/wp-json/wc/v3/products/tags/{tag_id}", json_body=body
        )
        return result  # type: ignore[return-value]

    async def delete_tag(self, tag_id: int, force: bool = True) -> dict[str, Any]:
        """Delete a product tag."""
        logger.debug("Calling delete_tag", tag_id=tag_id, force=force)
        params = {"force": "true"} if force else None
        result = await self.request(
            "DELETE", f"/wp-json/wc/v3/products/tags/{tag_id}", params=params
        )
        return result  # type: ignore[return-value]

    # 6. Attributes API (wc/v3/products/attributes)
    async def get_attribute(self, attribute_id: int) -> dict[str, Any]:
        """Fetch a product attribute."""
        logger.debug("Calling get_attribute", attribute_id=attribute_id)
        result = await self.request(
            "GET", f"/wp-json/wc/v3/products/attributes/{attribute_id}"
        )
        return result  # type: ignore[return-value]

    async def list_attributes(
        self, params: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """List product attributes."""
        logger.debug("Calling list_attributes", params=params)
        result = await self.request(
            "GET", "/wp-json/wc/v3/products/attributes", params=params
        )
        return result  # type: ignore[return-value]

    async def create_attribute(self, body: dict[str, Any]) -> dict[str, Any]:
        """Create a product attribute."""
        logger.debug("Calling create_attribute", name=body.get("name"))
        result = await self.request(
            "POST", "/wp-json/wc/v3/products/attributes", json_body=body
        )
        return result  # type: ignore[return-value]

    async def list_attribute_terms(
        self, attribute_id: int, params: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """List terms for a product attribute."""
        logger.debug("Calling list_attribute_terms", attribute_id=attribute_id)
        result = await self.request(
            "GET",
            f"/wp-json/wc/v3/products/attributes/{attribute_id}/terms",
            params=params,
        )
        return result  # type: ignore[return-value]

    async def create_attribute_term(
        self, attribute_id: int, body: dict[str, Any]
    ) -> dict[str, Any]:
        """Create a term for a product attribute."""
        logger.debug(
            "Calling create_attribute_term",
            attribute_id=attribute_id,
            name=body.get("name"),
        )
        result = await self.request(
            "POST",
            f"/wp-json/wc/v3/products/attributes/{attribute_id}/terms",
            json_body=body,
        )
        return result  # type: ignore[return-value]

    # 7. Media API (wp/v2/media)
    async def get_media(self, media_id: int) -> dict[str, Any]:
        """Fetch media object by ID."""
        logger.debug("Calling get_media", media_id=media_id)
        result = await self.request("GET", f"/wp-json/wp/v2/media/{media_id}")
        return result  # type: ignore[return-value]

    async def list_media(
        self, params: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """List media attachments."""
        logger.debug("Calling list_media", params=params)
        result = await self.request("GET", "/wp-json/wp/v2/media", params=params)
        return result  # type: ignore[return-value]

    async def create_media(
        self, filename: str, content_type: str, data: bytes
    ) -> dict[str, Any]:
        """Upload media binary to WordPress/WooCommerce media library."""
        logger.debug(
            "Calling create_media",
            filename=filename,
            content_type=content_type,
            byte_size=len(data),
        )
        files = {"file": (filename, data, content_type)}
        result = await self.request("POST", "/wp-json/wp/v2/media", files=files)
        return result  # type: ignore[return-value]

    async def delete_media(self, media_id: int, force: bool = True) -> dict[str, Any]:
        """Delete media asset."""
        logger.debug("Calling delete_media", media_id=media_id, force=force)
        params = {"force": "true"} if force else None
        result = await self.request(
            "DELETE", f"/wp-json/wp/v2/media/{media_id}", params=params
        )
        return result  # type: ignore[return-value]

    # 8. Webhooks API (wc/v3/webhooks)
    async def get_webhook(self, webhook_id: int) -> dict[str, Any]:
        """Fetch webhook definition."""
        logger.debug("Calling get_webhook", webhook_id=webhook_id)
        result = await self.request("GET", f"/wp-json/wc/v3/webhooks/{webhook_id}")
        return result  # type: ignore[return-value]

    async def list_webhooks(
        self, params: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """List configured WooCommerce webhooks."""
        logger.debug("Calling list_webhooks", params=params)
        result = await self.request("GET", "/wp-json/wc/v3/webhooks", params=params)
        return result  # type: ignore[return-value]

    async def create_webhook(self, body: dict[str, Any]) -> dict[str, Any]:
        """Register a new webhook subscription in WooCommerce."""
        logger.debug(
            "Calling create_webhook",
            topic=body.get("topic"),
            delivery_url=body.get("delivery_url"),
        )
        result = await self.request("POST", "/wp-json/wc/v3/webhooks", json_body=body)
        return result  # type: ignore[return-value]

    async def update_webhook(
        self, webhook_id: int, body: dict[str, Any]
    ) -> dict[str, Any]:
        """Update webhook configuration."""
        logger.debug("Calling update_webhook", webhook_id=webhook_id)
        result = await self.request(
            "PUT", f"/wp-json/wc/v3/webhooks/{webhook_id}", json_body=body
        )
        return result  # type: ignore[return-value]

    async def delete_webhook(
        self, webhook_id: int, force: bool = True
    ) -> dict[str, Any]:
        """Delete a webhook registration."""
        logger.debug("Calling delete_webhook", webhook_id=webhook_id, force=force)
        params = {"force": "true"} if force else None
        result = await self.request(
            "DELETE", f"/wp-json/wc/v3/webhooks/{webhook_id}", params=params
        )
        return result  # type: ignore[return-value]

    # 9. System Status API (wc/v3/system_status)
    async def get_system_status(self) -> dict[str, Any]:
        """Fetch WooCommerce system status and environment summary."""
        logger.debug("Calling get_system_status")
        result = await self.request("GET", "/wp-json/wc/v3/system_status")
        return result  # type: ignore[return-value]


# Backwards-compatible alias
WooCommerceAPIClient = WooCommerceClient

__all__ = ["WooCommerceAPIClient", "WooCommerceClient"]
