"""Root schemas for WooCommerce credentials and multi-tenant site context."""

from pydantic import AliasChoices, BaseModel, Field


class Credentials(BaseModel):
    """Resolved WooCommerce REST API credentials for a specific tenant and site."""

    site_url: str = Field(
        description="Base URL of the WordPress/WooCommerce site (e.g. https://store.example.com)"
    )
    consumer_key: str = Field(description="WooCommerce REST API Consumer Key (ck_...)")
    consumer_secret: str = Field(
        description="WooCommerce REST API Consumer Secret (cs_...)"
    )
    webhook_secret: str | None = Field(
        default=None, description="Optional HMAC-SHA256 signing secret for webhooks"
    )


class Site(BaseModel):
    """Multi-tenant site identity and routing parameters."""

    tenant_id: int | str = Field(
        description="Enterprise tenant identifier",
        validation_alias=AliasChoices("tenant_id", "tenantId"),
    )
    site_id: int | str = Field(
        default=1,
        description="Store or blog site identifier",
        validation_alias=AliasChoices("site_id", "channel_id", "siteId", "channelId"),
    )
    environment: str = Field(
        default="production", description="Site environment (e.g. production, staging)"
    )


__all__ = ["Credentials", "Site"]
