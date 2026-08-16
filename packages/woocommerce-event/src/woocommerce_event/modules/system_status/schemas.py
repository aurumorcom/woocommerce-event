"""System status domain schemas and CloudEvents definitions."""

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field
from python_event.modules.events.schemas import EventBaseModel, EventData


class EnvironmentInfo(BaseModel):
    """WooCommerce server and host runtime environment details."""

    home_url: str | None = Field(default=None, description="Home URL")
    site_url: str | None = Field(default=None, description="Site URL")
    version: str | None = Field(default=None, description="WooCommerce plugin version")
    wp_version: str | None = Field(default=None, description="WordPress core version")
    php_version: str | None = Field(default=None, description="PHP version")
    server_info: str | None = Field(default=None, description="Server software info")


class DatabaseInfo(BaseModel):
    """WooCommerce database engine and prefix details."""

    wc_database_version: str | None = Field(
        default=None, description="Database schema version"
    )
    database_prefix: str | None = Field(default=None, description="Table prefix")
    maxmind_geoip_database: str | None = Field(
        default=None, description="GeoIP database status"
    )


class SecurityInfo(BaseModel):
    """WooCommerce security checklist configuration."""

    secure_connection: bool = Field(default=True, description="HTTPS enabled")
    hide_errors: bool = Field(
        default=True, description="Error display disabled in production"
    )


class SystemStatus(EventData):
    """1:1 WooCommerce System Status Model."""

    environment: EnvironmentInfo | None = Field(
        default=None, description="Environment summary"
    )
    database: DatabaseInfo | None = Field(default=None, description="Database summary")
    security: SecurityInfo | None = Field(
        default=None, description="Security parameters"
    )
    settings: dict[str, Any] = Field(
        default_factory=dict, description="Store settings snapshot"
    )


class SystemStatusSampled(EventBaseModel):
    """CloudEvent emitted on periodic or on-demand health check sample."""

    type: str = Field(
        default="woocommerce.system_status.sampled", description="CloudEvents type"
    )
    source: str = Field(
        default="woocommerce://1/system_status", description="Context URI reference"
    )
    subject: str = Field(default="1", description="Numeric site identifier")
    time: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Event timestamp",
    )
    tenant_id: int | str = Field(
        default="default", description="Dedicated tenant extension attribute"
    )
    data: SystemStatus = Field(description="System status payload")


__all__ = [
    "DatabaseInfo",
    "EnvironmentInfo",
    "SecurityInfo",
    "SystemStatus",
    "SystemStatusSampled",
]
