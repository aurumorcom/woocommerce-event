"""Configuration settings for woocommerce-event."""

from pydantic import AliasChoices, BaseModel, Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from python_event.config import (
    ConfluentConfig,
    KafkaConfig,
    LoggingConfig,
    RisingWaveConfig,
)
from python_event.config import (
    EventSettings as PythonEventSettings,
)
from python_logging.config import LoggingSettings


class WooCommerceConfig(BaseModel):
    """Configuration for WooCommerce REST API bridge."""

    site_url: str | None = Field(
        default=None, description="Default WordPress/WooCommerce site base URL"
    )
    consumer_key: str | None = Field(
        default=None, description="Default WooCommerce Consumer Key"
    )
    consumer_secret: str | None = Field(
        default=None, description="Default WooCommerce Consumer Secret"
    )
    webhook_secret: str | None = Field(
        default=None, description="Shared webhook signature HMAC secret"
    )
    timeout_seconds: float = Field(
        default=30.0, description="HTTP client request timeout in seconds"
    )


class Settings(PythonEventSettings, LoggingSettings, BaseSettings):
    """Unified application settings combining python_event, python_logging, and WooCommerce configuration."""

    model_config = SettingsConfigDict(
        env_nested_delimiter="_",
        extra="ignore",
        env_file=(".env.test", ".env"),
        env_file_encoding="utf-8",
    )

    woocommerce_site_url: str | None = Field(
        default=None,
        validation_alias=AliasChoices("WOOCOMMERCE_SITE_URL", "woocommerce_site_url"),
    )
    woocommerce_consumer_key: str | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "WOOCOMMERCE_CONSUMER_KEY", "woocommerce_consumer_key"
        ),
    )
    woocommerce_consumer_secret: str | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "WOOCOMMERCE_CONSUMER_SECRET", "woocommerce_consumer_secret"
        ),
    )
    woocommerce_webhook_secret: str | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "WOOCOMMERCE_WEBHOOK_SECRET", "woocommerce_webhook_secret"
        ),
    )

    woocommerce: WooCommerceConfig = Field(default_factory=WooCommerceConfig)
    kafka: KafkaConfig = Field(default_factory=KafkaConfig)
    confluent: ConfluentConfig = Field(default_factory=ConfluentConfig)
    risingwave: RisingWaveConfig = Field(default_factory=RisingWaveConfig)
    logging_config: LoggingConfig = Field(default_factory=LoggingConfig)

    @model_validator(mode="after")
    def _validate_woocommerce_settings(self) -> "Settings":
        if self.woocommerce_site_url is not None:
            self.woocommerce.site_url = self.woocommerce_site_url
        if self.woocommerce_consumer_key is not None:
            self.woocommerce.consumer_key = self.woocommerce_consumer_key
        if self.woocommerce_consumer_secret is not None:
            self.woocommerce.consumer_secret = self.woocommerce_consumer_secret
        if self.woocommerce_webhook_secret is not None:
            self.woocommerce.webhook_secret = self.woocommerce_webhook_secret
        return self


settings = Settings()

__all__ = ["Settings", "WooCommerceConfig", "settings"]
