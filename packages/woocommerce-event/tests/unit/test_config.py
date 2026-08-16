"""Unit tests for configuration models."""

from woocommerce_event.config import Settings


def test_settings_defaults():
    """Test default values of Settings."""
    settings = Settings()
    assert settings.woocommerce is not None
    assert settings.woocommerce.timeout_seconds == 30.0
    assert settings.kafka is not None
    assert settings.confluent is not None
    assert settings.risingwave is not None


def test_settings_environment_override():
    """Test settings override with explicit kwargs."""
    settings = Settings(
        woocommerce_site_url="https://override.example.com",
        woocommerce_consumer_key="ck_override",
        woocommerce_consumer_secret="cs_override",
    )
    assert settings.woocommerce.site_url == "https://override.example.com"
    assert settings.woocommerce.consumer_key == "ck_override"
    assert settings.woocommerce.consumer_secret == "cs_override"
