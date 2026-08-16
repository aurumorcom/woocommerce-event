"""Unit tests for domain exception hierarchy."""

from woocommerce_event.exceptions import (
    CredentialsNotFoundError,
    WooCommerceAPIError,
    WooCommerceAuthenticationError,
    WooCommerceConfigurationError,
    WooCommerceError,
    WooCommercePublishError,
    WooCommerceRateLimitError,
    WooCommerceSerializationError,
)


def test_exception_inheritance():
    """Verify domain exceptions inherit from WooCommerceError."""
    assert issubclass(WooCommerceAPIError, WooCommerceError)
    assert issubclass(WooCommerceAuthenticationError, WooCommerceAPIError)
    assert issubclass(WooCommerceRateLimitError, WooCommerceAPIError)
    assert issubclass(WooCommerceConfigurationError, WooCommerceError)
    assert issubclass(WooCommerceSerializationError, WooCommerceError)
    assert issubclass(WooCommercePublishError, WooCommerceError)
    assert issubclass(CredentialsNotFoundError, WooCommerceError)
