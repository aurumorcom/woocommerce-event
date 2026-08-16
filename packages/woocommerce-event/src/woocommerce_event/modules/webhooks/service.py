"""Webhook domain transformation and service execution logic."""

import base64
import hashlib
import hmac
import uuid
from datetime import UTC, datetime
from typing import Any

import structlog

from woocommerce_event.integrations.woocommerce import WooCommerceClient
from woocommerce_event.modules.webhooks.schemas import (
    WebhookCreated,
    WebhookDeleted,
    WebhookSubscription,
    WebhookUpdated,
)

logger = structlog.get_logger(__name__)


def validate_webhook_hmac_signature(
    raw_payload: bytes, signature_header: str, secret: str
) -> bool:
    """Validate WooCommerce X-WC-Webhook-Signature HMAC-SHA256 signature."""
    logger.debug("Verifying HMAC-SHA256 signature for webhook payload")
    if not secret or not signature_header:
        logger.warning("Missing webhook secret or signature header for validation")
        return False

    computed_digest = hmac.new(
        secret.encode("utf-8"), raw_payload, hashlib.sha256
    ).digest()
    computed_signature = base64.b64encode(computed_digest).decode("utf-8")
    is_valid = hmac.compare_digest(computed_signature, signature_header)

    if is_valid:
        logger.info("Webhook HMAC signature validation succeeded")
    else:
        logger.error("Webhook HMAC signature validation failed")

    return is_valid


def parse_webhook_payload(
    raw_json: dict[str, Any],
    tenant_id: int | str,
    site_id: int | str = 1,
    action: str = "created",
) -> WebhookCreated | WebhookUpdated | WebhookDeleted:
    """Parse webhook subscription payload into a canonical CloudEvent."""
    logger.debug(
        "Parsing webhook subscription payload",
        tenant_id=tenant_id,
        site_id=site_id,
    )

    webhook = WebhookSubscription.model_validate(raw_json)
    event_id = str(uuid.uuid4())
    now = datetime.now(UTC)
    source = f"woocommerce://{site_id}/webhooks"
    subject = str(site_id)

    if action == "deleted":
        logger.info(
            "Created WebhookDeleted event",
            event_id=event_id,
            webhook_id=webhook.id,
            tenant_id=tenant_id,
        )
        return WebhookDeleted(
            id=event_id,
            source=source,
            subject=subject,
            time=now,
            tenant_id=tenant_id,
            data=webhook,
        )
    elif action == "updated":
        logger.info(
            "Created WebhookUpdated event",
            event_id=event_id,
            webhook_id=webhook.id,
            tenant_id=tenant_id,
        )
        return WebhookUpdated(
            id=event_id,
            source=source,
            subject=subject,
            time=now,
            tenant_id=tenant_id,
            data=webhook,
        )

    logger.info(
        "Created WebhookCreated event",
        event_id=event_id,
        webhook_id=webhook.id,
        tenant_id=tenant_id,
    )
    return WebhookCreated(
        id=event_id,
        source=source,
        subject=subject,
        time=now,
        tenant_id=tenant_id,
        data=webhook,
    )


async def provision_webhooks(
    client: WooCommerceClient,
    delivery_url: str,
    secret: str,
    topics: list[str] | None = None,
) -> list[dict[str, Any]]:
    """Provision standard WooCommerce inbound webhook subscriptions (defaults to order.created, order.updated)."""
    target_topics = topics or [
        "order.created",
        "order.updated",
    ]
    logger.info(
        "Provisioning standard WooCommerce webhook subscriptions",
        delivery_url=delivery_url,
        topics=target_topics,
    )

    results: list[dict[str, Any]] = []
    for topic in target_topics:
        payload = {
            "name": f"Event Stream: {topic}",
            "topic": topic,
            "delivery_url": delivery_url,
            "secret": secret,
            "status": "active",
        }
        res = await client.create_webhook(payload)
        logger.info(
            "Registered webhook subscription",
            topic=topic,
            webhook_id=res.get("id"),
        )
        results.append(res)

    logger.info("Webhooks registered successfully", total_registered=len(results))
    return results


__all__ = [
    "parse_webhook_payload",
    "provision_webhooks",
    "validate_webhook_hmac_signature",
]
