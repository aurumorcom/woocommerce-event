"""Attribute and Term domain schemas and CloudEvents definitions."""

from datetime import UTC, datetime

from pydantic import Field
from python_event.modules.events.schemas import EventBaseModel, EventData

from woocommerce_event.constants import (
    EVENT_TYPE_ITEM_ATTRIBUTE_CREATED,
    EVENT_TYPE_ITEM_ATTRIBUTE_DELETED,
    EVENT_TYPE_ITEM_ATTRIBUTE_UPDATED,
    EVENT_TYPE_ITEM_ATTRIBUTE_VALUE_CREATED,
    EVENT_TYPE_ITEM_ATTRIBUTE_VALUE_DELETED,
    EVENT_TYPE_ITEM_ATTRIBUTE_VALUE_UPDATED,
)


class AttributeTerm(EventData):
    """Product attribute term representation."""

    id: int | None = Field(default=None, description="Term ID")
    name: str = Field(description="Term name")
    slug: str | None = Field(default=None, description="Term URL slug")
    description: str | None = Field(default=None, description="Term description")
    menu_order: int = Field(default=0, description="Sort order")
    count: int = Field(default=0, description="Product count")


class Attribute(EventData):
    """1:1 WooCommerce Product Attribute Model."""

    id: int | None = Field(default=None, description="Attribute ID")
    name: str = Field(description="Attribute name")
    slug: str | None = Field(default=None, description="Attribute slug")
    type: str = Field(default="select", description="Attribute type")
    order_by: str = Field(default="menu_order", description="Sort order criteria")
    has_archives: bool = Field(
        default=False, description="Enable archives for attribute"
    )


class AttributeCreated(EventBaseModel):
    """CloudEvent emitted when a product attribute is created."""

    type: str = Field(
        default=EVENT_TYPE_ITEM_ATTRIBUTE_CREATED, description="CloudEvents type"
    )
    source: str = Field(
        default="woocommerce://1/attributes", description="Context URI reference"
    )
    subject: str = Field(default="1", description="Numeric site identifier")
    time: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Event timestamp",
    )
    tenant_id: int | str = Field(
        default="default", description="Dedicated tenant extension attribute"
    )
    data: Attribute = Field(description="Attribute data payload")


class AttributeUpdated(EventBaseModel):
    """CloudEvent emitted when a product attribute is updated."""

    type: str = Field(
        default=EVENT_TYPE_ITEM_ATTRIBUTE_UPDATED, description="CloudEvents type"
    )
    source: str = Field(
        default="woocommerce://1/attributes", description="Context URI reference"
    )
    subject: str = Field(default="1", description="Numeric site identifier")
    time: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Event timestamp",
    )
    tenant_id: int | str = Field(
        default="default", description="Dedicated tenant extension attribute"
    )
    data: Attribute = Field(description="Attribute data payload")


class AttributeDeleted(EventBaseModel):
    """CloudEvent emitted when a product attribute is deleted."""

    type: str = Field(
        default=EVENT_TYPE_ITEM_ATTRIBUTE_DELETED, description="CloudEvents type"
    )
    source: str = Field(
        default="woocommerce://1/attributes", description="Context URI reference"
    )
    subject: str = Field(default="1", description="Numeric site identifier")
    time: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Event timestamp",
    )
    tenant_id: int | str = Field(
        default="default", description="Dedicated tenant extension attribute"
    )
    data: Attribute = Field(description="Attribute data payload")


class AttributeTermCreated(EventBaseModel):
    """CloudEvent emitted when an attribute term is created."""

    type: str = Field(
        default=EVENT_TYPE_ITEM_ATTRIBUTE_VALUE_CREATED, description="CloudEvents type"
    )
    source: str = Field(
        default="woocommerce://1/attributes/terms", description="Context URI reference"
    )
    subject: str = Field(default="1", description="Numeric site identifier")
    time: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Event timestamp",
    )
    tenant_id: int | str = Field(
        default="default", description="Dedicated tenant extension attribute"
    )
    data: AttributeTerm = Field(description="Attribute term data payload")


class AttributeTermUpdated(EventBaseModel):
    """CloudEvent emitted when an attribute term is updated."""

    type: str = Field(
        default=EVENT_TYPE_ITEM_ATTRIBUTE_VALUE_UPDATED, description="CloudEvents type"
    )
    source: str = Field(
        default="woocommerce://1/attributes/terms", description="Context URI reference"
    )
    subject: str = Field(default="1", description="Numeric site identifier")
    time: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Event timestamp",
    )
    tenant_id: int | str = Field(
        default="default", description="Dedicated tenant extension attribute"
    )
    data: AttributeTerm = Field(description="Attribute term data payload")


class AttributeTermDeleted(EventBaseModel):
    """CloudEvent emitted when an attribute term is deleted."""

    type: str = Field(
        default=EVENT_TYPE_ITEM_ATTRIBUTE_VALUE_DELETED, description="CloudEvents type"
    )
    source: str = Field(
        default="woocommerce://1/attributes/terms", description="Context URI reference"
    )
    subject: str = Field(default="1", description="Numeric site identifier")
    time: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Event timestamp",
    )
    tenant_id: int | str = Field(
        default="default", description="Dedicated tenant extension attribute"
    )
    data: AttributeTerm = Field(description="Attribute term data payload")


ItemAttribute = Attribute
ItemAttributeValue = AttributeTerm
AttributeValueCreated = AttributeTermCreated
AttributeValueUpdated = AttributeTermUpdated
AttributeValueDeleted = AttributeTermDeleted

__all__ = [
    "Attribute",
    "AttributeCreated",
    "AttributeDeleted",
    "AttributeTerm",
    "AttributeTermCreated",
    "AttributeTermDeleted",
    "AttributeTermUpdated",
    "AttributeUpdated",
    "AttributeValueCreated",
    "AttributeValueDeleted",
    "AttributeValueUpdated",
    "ItemAttribute",
    "ItemAttributeValue",
]
