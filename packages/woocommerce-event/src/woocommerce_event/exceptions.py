"""Domain exceptions for woocommerce-event."""


class WooCommerceError(Exception):
    """Root exception for all woocommerce-event errors."""


class WooCommerceAPIError(WooCommerceError):
    """Raised when WooCommerce REST API returns an error response."""


class WooCommerceAuthenticationError(WooCommerceAPIError):
    """Raised when WooCommerce REST API authentication fails (401/403)."""


class WooCommerceRateLimitError(WooCommerceAPIError):
    """Raised when WooCommerce REST API rate limit (429) is exceeded."""


class WooCommerceConfigurationError(WooCommerceError):
    """Raised when configuration is invalid or missing."""


class WooCommerceSerializationError(WooCommerceError):
    """Raised when serialization or deserialization of payloads/CloudEvents fails."""


class WooCommercePublishError(WooCommerceError):
    """Raised when event publishing to Kafka fails."""


class CredentialsNotFoundError(WooCommerceError):
    """Raised when credentials cannot be resolved for a given tenant/site."""


__all__ = [
    "CredentialsNotFoundError",
    "WooCommerceAPIError",
    "WooCommerceAuthenticationError",
    "WooCommerceConfigurationError",
    "WooCommerceError",
    "WooCommercePublishError",
    "WooCommerceRateLimitError",
    "WooCommerceSerializationError",
]
