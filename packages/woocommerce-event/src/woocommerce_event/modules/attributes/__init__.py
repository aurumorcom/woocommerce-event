"""Attributes domain module."""

from woocommerce_event.modules.attributes import schemas, service
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
from woocommerce_event.modules.attributes.service import (
    parse_attribute_term_webhook,
    parse_attribute_webhook,
    submit_attribute,
    submit_attribute_term,
)

__all__ = [
    "Attribute",
    "AttributeCreated",
    "AttributeDeleted",
    "AttributeTerm",
    "AttributeTermCreated",
    "AttributeTermDeleted",
    "AttributeTermUpdated",
    "AttributeUpdated",
    "parse_attribute_term_webhook",
    "parse_attribute_webhook",
    "schemas",
    "service",
    "submit_attribute",
    "submit_attribute_term",
]
