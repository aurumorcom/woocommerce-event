"""Products domain module."""

from woocommerce_event.modules.products import schemas, service
from woocommerce_event.modules.products.schemas import (
    Product,
    ProductAttribute,
    ProductCreated,
    ProductDeleted,
    ProductDimensions,
    ProductDownload,
    ProductImage,
    ProductUpdated,
)
from woocommerce_event.modules.products.service import (
    parse_product_webhook,
    submit_product,
)

__all__ = [
    "Product",
    "ProductAttribute",
    "ProductCreated",
    "ProductDeleted",
    "ProductDimensions",
    "ProductDownload",
    "ProductImage",
    "ProductUpdated",
    "parse_product_webhook",
    "schemas",
    "service",
    "submit_product",
]
