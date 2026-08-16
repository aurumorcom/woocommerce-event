"""Product variations domain module."""

from woocommerce_event.modules.variations import schemas, service
from woocommerce_event.modules.variations.schemas import (
    Variation,
    VariationAttribute,
    VariationCreated,
    VariationDeleted,
    VariationDimensions,
    VariationImage,
    VariationUpdated,
)
from woocommerce_event.modules.variations.service import (
    parse_variation_webhook,
    submit_variation,
)

__all__ = [
    "Variation",
    "VariationAttribute",
    "VariationCreated",
    "VariationDeleted",
    "VariationDimensions",
    "VariationImage",
    "VariationUpdated",
    "parse_variation_webhook",
    "schemas",
    "service",
    "submit_variation",
]
