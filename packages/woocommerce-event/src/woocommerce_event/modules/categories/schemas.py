"""Category domain schemas and CloudEvents definitions."""

from datetime import UTC, datetime

from pydantic import BaseModel, Field
from python_event.modules.events.schemas import EventBaseModel, EventData

from woocommerce_event.constants import (
    EVENT_TYPE_ITEM_CATEGORY_CREATED,
    EVENT_TYPE_ITEM_CATEGORY_DELETED,
    EVENT_TYPE_ITEM_CATEGORY_UPDATED,
)


class CategoryImage(BaseModel):
    """Category banner/thumbnail image."""

    id: int | None = Field(default=None, description="Image ID")
    src: str | None = Field(default=None, description="Image URL")
    name: str | None = Field(default=None, description="Image name")
    alt: str | None = Field(default=None, description="Image alt text")


class Category(EventData):
    """1:1 WooCommerce Product Category Model."""

    id: int | None = Field(default=None, description="Category ID")
    name: str = Field(description="Category name")
    slug: str | None = Field(default=None, description="Category URL slug")
    parent: int = Field(default=0, description="Parent category ID (0 for root)")
    description: str | None = Field(default=None, description="Category description")
    display: str = Field(default="default", description="Category display type")
    image: CategoryImage | None = Field(default=None, description="Category image")
    menu_order: int = Field(default=0, description="Category sort order")
    count: int = Field(default=0, description="Product count in this category")


class CategoryCreated(EventBaseModel):
    """CloudEvent emitted when a product category is created."""

    type: str = Field(
        default=EVENT_TYPE_ITEM_CATEGORY_CREATED, description="CloudEvents type"
    )
    source: str = Field(
        default="woocommerce://1/categories", description="Context URI reference"
    )
    subject: str = Field(default="1", description="Numeric site identifier")
    time: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Event timestamp",
    )
    tenant_id: int | str = Field(
        default="default", description="Dedicated tenant extension attribute"
    )
    data: Category = Field(description="Category data payload")


class CategoryUpdated(EventBaseModel):
    """CloudEvent emitted when a product category is updated."""

    type: str = Field(
        default=EVENT_TYPE_ITEM_CATEGORY_UPDATED, description="CloudEvents type"
    )
    source: str = Field(
        default="woocommerce://1/categories", description="Context URI reference"
    )
    subject: str = Field(default="1", description="Numeric site identifier")
    time: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Event timestamp",
    )
    tenant_id: int | str = Field(
        default="default", description="Dedicated tenant extension attribute"
    )
    data: Category = Field(description="Category data payload")


class CategoryDeleted(EventBaseModel):
    """CloudEvent emitted when a product category is deleted."""

    type: str = Field(
        default=EVENT_TYPE_ITEM_CATEGORY_DELETED, description="CloudEvents type"
    )
    source: str = Field(
        default="woocommerce://1/categories", description="Context URI reference"
    )
    subject: str = Field(default="1", description="Numeric site identifier")
    time: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Event timestamp",
    )
    tenant_id: int | str = Field(
        default="default", description="Dedicated tenant extension attribute"
    )
    data: Category = Field(description="Category data payload")


ItemCategory = Category

__all__ = [
    "Category",
    "CategoryCreated",
    "CategoryDeleted",
    "CategoryImage",
    "CategoryUpdated",
    "ItemCategory",
]
