"""Product domain schemas and CloudEvents definitions."""

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field
from python_event.modules.events.schemas import EventBaseModel, EventData

from woocommerce_event.constants import (
    EVENT_TYPE_PRODUCT_CREATED,
    EVENT_TYPE_PRODUCT_DELETED,
    EVENT_TYPE_PRODUCT_UPDATED,
)


class ProductDimensions(BaseModel):
    """Product physical dimensions."""

    length: str | None = Field(default=None, description="Product length in cm/in")
    width: str | None = Field(default=None, description="Product width in cm/in")
    height: str | None = Field(default=None, description="Product height in cm/in")


class ProductImage(BaseModel):
    """Product image reference."""

    id: int | None = Field(default=None, description="WordPress attachment ID")
    src: str = Field(description="Image URL")
    name: str | None = Field(default=None, description="Image name")
    alt: str | None = Field(default=None, description="Image alt text")


class ProductAttribute(BaseModel):
    """Product attribute specification."""

    id: int | None = Field(default=None, description="Attribute ID")
    name: str = Field(description="Attribute name")
    position: int = Field(default=0, description="Attribute sort position")
    visible: bool = Field(default=True, description="Visible on product page")
    variation: bool = Field(default=False, description="Used for variation generation")
    options: list[str] = Field(
        default_factory=list, description="Attribute option values"
    )


class ProductDownload(BaseModel):
    """Product downloadable file item."""

    id: str | None = Field(default=None, description="Downloadable file ID")
    name: str = Field(description="Download name")
    file: str = Field(description="Download file URL")


class Product(EventData):
    """1:1 WooCommerce REST API Product Model."""

    id: int | None = Field(default=None, description="Unique product ID")
    name: str = Field(description="Product title/name")
    slug: str | None = Field(default=None, description="Product URL slug")
    type: str = Field(
        default="simple",
        description="Product type (simple, grouped, external, variable)",
    )
    status: str = Field(
        default="publish",
        description="Product status (draft, pending, private, publish)",
    )
    featured: bool = Field(default=False, description="Featured product flag")
    catalog_visibility: str = Field(
        default="visible",
        description="Catalog visibility (visible, catalog, search, hidden)",
    )
    description: str | None = Field(
        default=None, description="Product description (HTML allowed)"
    )
    short_description: str | None = Field(
        default=None, description="Product short description"
    )
    sku: str | None = Field(default=None, description="Unique Stock Keeping Unit")
    price: str | None = Field(default=None, description="Current active price")
    regular_price: str | None = Field(default=None, description="Product regular price")
    sale_price: str | None = Field(default=None, description="Product sale price")
    manage_stock: bool = Field(
        default=False, description="Manage stock level at product level"
    )
    stock_quantity: int | None = Field(
        default=None, description="Stock quantity inventory count"
    )
    stock_status: str = Field(
        default="instock", description="Stock status (instock, outofstock, onbackorder)"
    )
    weight: str | None = Field(default=None, description="Product weight")
    dimensions: ProductDimensions | None = Field(
        default=None, description="Product dimensions"
    )
    images: list[ProductImage] = Field(
        default_factory=list, description="List of product images"
    )
    attributes: list[ProductAttribute] = Field(
        default_factory=list, description="List of product attributes"
    )
    categories: list[dict[str, Any]] = Field(
        default_factory=list, description="Categories list"
    )
    tags: list[dict[str, Any]] = Field(default_factory=list, description="Tags list")
    variations: list[int] = Field(
        default_factory=list, description="List of variation IDs"
    )


class ProductCreated(EventBaseModel):
    """CloudEvent emitted when a WooCommerce product is created."""

    type: str = Field(
        default=EVENT_TYPE_PRODUCT_CREATED, description="CloudEvents type"
    )
    source: str = Field(
        default="woocommerce://1/products", description="Context URI reference"
    )
    subject: str = Field(default="1", description="Numeric site identifier")
    time: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Event timestamp",
    )
    tenant_id: int | str = Field(
        default="default", description="Dedicated tenant extension attribute"
    )
    data: Product = Field(description="Product data payload")


class ProductUpdated(EventBaseModel):
    """CloudEvent emitted when a WooCommerce product is updated."""

    type: str = Field(
        default=EVENT_TYPE_PRODUCT_UPDATED, description="CloudEvents type"
    )
    source: str = Field(
        default="woocommerce://1/products", description="Context URI reference"
    )
    subject: str = Field(default="1", description="Numeric site identifier")
    time: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Event timestamp",
    )
    tenant_id: int | str = Field(
        default="default", description="Dedicated tenant extension attribute"
    )
    data: Product = Field(description="Product data payload")


class ProductDeleted(EventBaseModel):
    """CloudEvent emitted when a WooCommerce product is deleted."""

    type: str = Field(
        default=EVENT_TYPE_PRODUCT_DELETED, description="CloudEvents type"
    )
    source: str = Field(
        default="woocommerce://1/products", description="Context URI reference"
    )
    subject: str = Field(default="1", description="Numeric site identifier")
    time: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Event timestamp",
    )
    tenant_id: int | str = Field(
        default="default", description="Dedicated tenant extension attribute"
    )
    data: Product = Field(description="Product data payload")


__all__ = [
    "Product",
    "ProductAttribute",
    "ProductCreated",
    "ProductDeleted",
    "ProductDimensions",
    "ProductDownload",
    "ProductImage",
    "ProductUpdated",
]
