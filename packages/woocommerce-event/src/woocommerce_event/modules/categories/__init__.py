"""Categories domain module."""

from woocommerce_event.modules.categories import schemas, service
from woocommerce_event.modules.categories.schemas import (
    Category,
    CategoryCreated,
    CategoryDeleted,
    CategoryImage,
    CategoryUpdated,
)
from woocommerce_event.modules.categories.service import (
    parse_category_webhook,
    submit_category,
)

__all__ = [
    "Category",
    "CategoryCreated",
    "CategoryDeleted",
    "CategoryImage",
    "CategoryUpdated",
    "parse_category_webhook",
    "schemas",
    "service",
    "submit_category",
]
