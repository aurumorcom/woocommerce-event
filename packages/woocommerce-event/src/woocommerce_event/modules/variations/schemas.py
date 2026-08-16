"""Variation domain schemas and CloudEvents definitions."""

from datetime import UTC, datetime

from pydantic import BaseModel, Field
from python_event.modules.events.schemas import EventBaseModel, EventData

from woocommerce_event.constants import (
    EVENT_TYPE_PRODUCT_VARIANT_CREATED,
    EVENT_TYPE_PRODUCT_VARIANT_DELETED,
    EVENT_TYPE_PRODUCT_VARIANT_UPDATED,
)


class VariationAttribute(BaseModel):
    """Variation specific attribute specification."""

    id: int | None = Field(default=None, description="Attribute ID")
    name: str = Field(description="Attribute name (e.g. Color, Size)")
    option: str = Field(description="Selected attribute option (e.g. Red, Large)")


class VariationDimensions(BaseModel):
    """Variation dimensions."""

    length: str | None = Field(default=None, description="Length")
    width: str | None = Field(default=None, description="Width")
    height: str | None = Field(default=None, description="Height")


class VariationImage(BaseModel):
    """Variation image."""

    id: int | None = Field(default=None, description="Image ID")
    src: str | None = Field(default=None, description="Image source URL")
    name: str | None = Field(default=None, description="Image name")
    alt: str | None = Field(default=None, description="Image alt text")


class Variation(EventData):
    """1:1 WooCommerce Product Variation Model."""

    id: int | None = Field(default=None, description="Variation ID")
    parent_id: int | None = Field(default=None, description="Parent product ID")
    sku: str | None = Field(default=None, description="Variation SKU")
    price: str | None = Field(default=None, description="Active price")
    regular_price: str | None = Field(default=None, description="Regular price")
    sale_price: str | None = Field(default=None, description="Sale price")
    status: str = Field(default="publish", description="Variation status")
    manage_stock: bool = Field(
        default=False, description="Manage stock at variation level"
    )
    stock_quantity: int | None = Field(default=None, description="Stock quantity")
    stock_status: str = Field(default="instock", description="Stock status")
    weight: str | None = Field(default=None, description="Variation weight")
    dimensions: VariationDimensions | None = Field(
        default=None, description="Dimensions"
    )
    image: VariationImage | None = Field(default=None, description="Variation image")
    attributes: list[VariationAttribute] = Field(
        default_factory=list, description="Variation attribute terms"
    )


class VariationCreated(EventBaseModel):
    """CloudEvent emitted when a product variation is created."""

    type: str = Field(
        default=EVENT_TYPE_PRODUCT_VARIANT_CREATED, description="CloudEvents type"
    )
    source: str = Field(
        default="woocommerce://1/variations", description="Context URI reference"
    )
    subject: str = Field(default="1", description="Numeric site identifier")
    time: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Event timestamp",
    )
    tenant_id: int | str = Field(
        default="default", description="Dedicated tenant extension attribute"
    )
    data: Variation = Field(description="Variation data payload")


class VariationUpdated(EventBaseModel):
    """CloudEvent emitted when a product variation is updated."""

    type: str = Field(
        default=EVENT_TYPE_PRODUCT_VARIANT_UPDATED, description="CloudEvents type"
    )
    source: str = Field(
        default="woocommerce://1/variations", description="Context URI reference"
    )
    subject: str = Field(default="1", description="Numeric site identifier")
    time: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Event timestamp",
    )
    tenant_id: int | str = Field(
        default="default", description="Dedicated tenant extension attribute"
    )
    data: Variation = Field(description="Variation data payload")


class VariationDeleted(EventBaseModel):
    """CloudEvent emitted when a product variation is deleted."""

    type: str = Field(
        default=EVENT_TYPE_PRODUCT_VARIANT_DELETED, description="CloudEvents type"
    )
    source: str = Field(
        default="woocommerce://1/variations", description="Context URI reference"
    )
    subject: str = Field(default="1", description="Numeric site identifier")
    time: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Event timestamp",
    )
    tenant_id: int | str = Field(
        default="default", description="Dedicated tenant extension attribute"
    )
    data: Variation = Field(description="Variation data payload")


ProductVariant = Variation

__all__ = [
    "ProductVariant",
    "Variation",
    "VariationAttribute",
    "VariationCreated",
    "VariationDeleted",
    "VariationDimensions",
    "VariationImage",
    "VariationUpdated",
]
