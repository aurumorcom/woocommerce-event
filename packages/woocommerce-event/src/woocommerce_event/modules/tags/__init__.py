"""Tags domain module."""

from woocommerce_event.modules.tags import schemas, service
from woocommerce_event.modules.tags.schemas import (
    Tag,
    TagCreated,
    TagDeleted,
    TagUpdated,
)
from woocommerce_event.modules.tags.service import (
    parse_tag_webhook,
    submit_tag,
)

__all__ = [
    "Tag",
    "TagCreated",
    "TagDeleted",
    "TagUpdated",
    "parse_tag_webhook",
    "schemas",
    "service",
    "submit_tag",
]
