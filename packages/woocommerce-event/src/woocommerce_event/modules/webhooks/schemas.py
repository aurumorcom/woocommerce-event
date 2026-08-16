"""Webhook subscription domain schemas and CloudEvents definitions."""

from datetime import UTC, datetime

from pydantic import BaseModel, Field
from python_event.modules.events.schemas import EventBaseModel, EventData


class WebhookSubscription(EventData):
    """1:1 WooCommerce Webhook Subscription Model."""

    id: int | None = Field(default=None, description="Webhook ID")
    name: str = Field(description="Webhook name")
    status: str = Field(
        default="active", description="Webhook status (active, paused, disabled)"
    )
    topic: str = Field(
        description="Webhook event topic (e.g. product.created, order.updated)"
    )
    resource: str | None = Field(default=None, description="Resource type")
    event: str | None = Field(default=None, description="Event action")
    hooks: list[str] = Field(
        default_factory=list, description="Associated WooCommerce action hooks"
    )
    delivery_url: str = Field(description="Webhook payload delivery target URL")
    secret: str | None = Field(default=None, description="HMAC-SHA256 signature secret")
    date_created: str | None = Field(
        default=None, description="Date subscription was created"
    )


class WebhookDeliveryLog(BaseModel):
    """Webhook delivery attempt execution log."""

    id: int | None = Field(default=None, description="Delivery ID")
    duration: str | None = Field(default=None, description="Execution duration")
    summary: str | None = Field(default=None, description="Execution summary")
    request_headers: dict[str, str] = Field(
        default_factory=dict, description="Headers sent with webhook"
    )
    request_body: str | None = Field(default=None, description="Body sent")
    response_code: int | None = Field(default=None, description="HTTP status response")
    response_message: str | None = Field(
        default=None, description="HTTP response message"
    )


class WebhookCreated(EventBaseModel):
    """CloudEvent emitted when a webhook registration is created."""

    type: str = Field(
        default="woocommerce.webhook.created", description="CloudEvents type"
    )
    source: str = Field(
        default="woocommerce://1/webhooks", description="Context URI reference"
    )
    subject: str = Field(default="1", description="Numeric site identifier")
    time: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Event timestamp",
    )
    tenant_id: int | str = Field(
        default="default", description="Dedicated tenant extension attribute"
    )
    data: WebhookSubscription = Field(description="Webhook subscription payload")


class WebhookUpdated(EventBaseModel):
    """CloudEvent emitted when a webhook registration is updated."""

    type: str = Field(
        default="woocommerce.webhook.updated", description="CloudEvents type"
    )
    source: str = Field(
        default="woocommerce://1/webhooks", description="Context URI reference"
    )
    subject: str = Field(default="1", description="Numeric site identifier")
    time: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Event timestamp",
    )
    tenant_id: int | str = Field(
        default="default", description="Dedicated tenant extension attribute"
    )
    data: WebhookSubscription = Field(description="Webhook subscription payload")


class WebhookDeleted(EventBaseModel):
    """CloudEvent emitted when a webhook registration is deleted."""

    type: str = Field(
        default="woocommerce.webhook.deleted", description="CloudEvents type"
    )
    source: str = Field(
        default="woocommerce://1/webhooks", description="Context URI reference"
    )
    subject: str = Field(default="1", description="Numeric site identifier")
    time: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Event timestamp",
    )
    tenant_id: int | str = Field(
        default="default", description="Dedicated tenant extension attribute"
    )
    data: WebhookSubscription = Field(description="Webhook subscription payload")


__all__ = [
    "WebhookCreated",
    "WebhookDeleted",
    "WebhookDeliveryLog",
    "WebhookSubscription",
    "WebhookUpdated",
]
