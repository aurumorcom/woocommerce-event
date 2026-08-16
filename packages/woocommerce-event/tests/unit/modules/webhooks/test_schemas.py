"""Unit tests for webhook schemas."""

from fixtures.woocommerce_api_samples import SAMPLE_WEBHOOK_RAW
from woocommerce_event.modules.webhooks.schemas import (
    WebhookCreated,
    WebhookSubscription,
)


def test_webhook_model_validation():
    """Test validating sample WooCommerce webhook subscription."""
    webhook = WebhookSubscription.model_validate(SAMPLE_WEBHOOK_RAW)
    assert webhook.id == 10
    assert webhook.topic == "order.created"
    assert webhook.status == "active"


def test_webhook_created_cloudevent():
    """Test WebhookCreated CloudEvent schema."""
    webhook = WebhookSubscription.model_validate(SAMPLE_WEBHOOK_RAW)
    event = WebhookCreated(
        id="evt-wh-1",
        source="woocommerce://101/webhooks",
        subject="101",
        tenant_id=1,
        data=webhook,
    )
    assert event.type == "woocommerce.webhook.created"
    assert event.subject == "101"
    assert event.tenant_id == 1
    assert event.data.id == 10
