"""Attribute and Term domain transformation and service execution logic."""

import uuid
from datetime import UTC, datetime
from typing import Any

import structlog

from woocommerce_event.integrations.woocommerce import WooCommerceClient
from woocommerce_event.modules.attributes.schemas import (
    Attribute,
    AttributeCreated,
    AttributeDeleted,
    AttributeTerm,
    AttributeTermCreated,
    AttributeTermDeleted,
    AttributeTermUpdated,
    AttributeUpdated,
)

logger = structlog.get_logger(__name__)


def parse_attribute_webhook(
    raw_json: dict[str, Any],
    tenant_id: int | str,
    site_id: int | str = 1,
    action: str = "created",
) -> AttributeCreated | AttributeUpdated | AttributeDeleted:
    """Parse raw attribute webhook payload into a canonical CloudEvent."""
    logger.debug(
        "Parsing attribute webhook payload",
        tenant_id=tenant_id,
        site_id=site_id,
        attr_id=raw_json.get("id"),
    )

    attr = Attribute.model_validate(raw_json)
    event_id = str(uuid.uuid4())
    now = datetime.now(UTC)
    source = f"woocommerce://{site_id}/attributes"
    subject = str(site_id)

    if action == "deleted":
        logger.info(
            "Created AttributeDeleted event",
            event_id=event_id,
            attr_id=attr.id,
            tenant_id=tenant_id,
        )
        return AttributeDeleted(
            id=event_id,
            source=source,
            subject=subject,
            time=now,
            tenant_id=tenant_id,
            data=attr,
        )
    elif action == "updated":
        logger.info(
            "Created AttributeUpdated event",
            event_id=event_id,
            attr_id=attr.id,
            tenant_id=tenant_id,
        )
        return AttributeUpdated(
            id=event_id,
            source=source,
            subject=subject,
            time=now,
            tenant_id=tenant_id,
            data=attr,
        )

    logger.info(
        "Created AttributeCreated event",
        event_id=event_id,
        attr_id=attr.id,
        tenant_id=tenant_id,
    )
    return AttributeCreated(
        id=event_id,
        source=source,
        subject=subject,
        time=now,
        tenant_id=tenant_id,
        data=attr,
    )


def parse_attribute_term_webhook(
    raw_json: dict[str, Any],
    attribute_id: int,
    tenant_id: int | str,
    site_id: int | str = 1,
    action: str = "created",
) -> AttributeTermCreated | AttributeTermUpdated | AttributeTermDeleted:
    """Parse raw attribute term webhook payload into a canonical CloudEvent."""
    logger.debug(
        "Parsing attribute term webhook payload",
        attribute_id=attribute_id,
        tenant_id=tenant_id,
        site_id=site_id,
        term_id=raw_json.get("id"),
    )

    term = AttributeTerm.model_validate(raw_json)
    event_id = str(uuid.uuid4())
    now = datetime.now(UTC)
    source = f"woocommerce://{site_id}/attributes/{attribute_id}/terms"
    subject = str(site_id)

    if action == "deleted":
        logger.info(
            "Created AttributeTermDeleted event",
            event_id=event_id,
            term_id=term.id,
            tenant_id=tenant_id,
        )
        return AttributeTermDeleted(
            id=event_id,
            source=source,
            subject=subject,
            time=now,
            tenant_id=tenant_id,
            data=term,
        )
    elif action == "updated":
        logger.info(
            "Created AttributeTermUpdated event",
            event_id=event_id,
            term_id=term.id,
            tenant_id=tenant_id,
        )
        return AttributeTermUpdated(
            id=event_id,
            source=source,
            subject=subject,
            time=now,
            tenant_id=tenant_id,
            data=term,
        )

    logger.info(
        "Created AttributeTermCreated event",
        event_id=event_id,
        term_id=term.id,
        tenant_id=tenant_id,
    )
    return AttributeTermCreated(
        id=event_id,
        source=source,
        subject=subject,
        time=now,
        tenant_id=tenant_id,
        data=term,
    )


async def upsert_attribute(
    client: WooCommerceClient, attr: Attribute
) -> dict[str, Any]:
    """Upsert attribute in WooCommerce with clean 1:1 serialization."""
    logger.info("Upserting attribute to WooCommerce", name=attr.name)
    body = attr.model_dump(exclude_unset=True, exclude_none=True)

    result = await client.create_attribute(body)
    logger.info("Attribute upserted successfully", attribute_id=result.get("id"))
    return result


async def upsert_attribute_term(
    client: WooCommerceClient, attribute_id: int, term: AttributeTerm
) -> dict[str, Any]:
    """Upsert attribute term to WooCommerce with clean 1:1 serialization."""
    logger.info(
        "Upserting attribute term to WooCommerce",
        attribute_id=attribute_id,
        name=term.name,
    )
    body = term.model_dump(exclude_unset=True, exclude_none=True)

    result = await client.create_attribute_term(attribute_id, body)
    logger.info(
        "Attribute term upserted successfully",
        attribute_id=attribute_id,
        term_id=result.get("id"),
    )
    return result


submit_attribute = upsert_attribute
submit_attribute_term = upsert_attribute_term

__all__ = [
    "parse_attribute_term_webhook",
    "parse_attribute_webhook",
    "submit_attribute",
    "submit_attribute_term",
    "upsert_attribute",
    "upsert_attribute_term",
]
