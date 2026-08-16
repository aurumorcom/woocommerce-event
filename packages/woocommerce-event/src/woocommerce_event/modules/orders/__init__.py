"""Orders domain module."""

from woocommerce_event.modules.orders import schemas, service
from woocommerce_event.modules.orders.schemas import (
    Order,
    OrderBilling,
    OrderCancelled,
    OrderCreated,
    OrderItem,
    OrderShipping,
    OrderTaxLine,
    OrderUpdated,
)
from woocommerce_event.modules.orders.service import (
    fetch_order_details,
    parse_order_webhook,
    submit_order,
)

__all__ = [
    "Order",
    "OrderBilling",
    "OrderCancelled",
    "OrderCreated",
    "OrderItem",
    "OrderShipping",
    "OrderTaxLine",
    "OrderUpdated",
    "fetch_order_details",
    "parse_order_webhook",
    "schemas",
    "service",
    "submit_order",
]
