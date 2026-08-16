"""Order domain schemas and CloudEvents definitions."""

from datetime import UTC, datetime

from pydantic import BaseModel, Field
from python_event.modules.events.schemas import EventBaseModel, EventData

from woocommerce_event.constants import (
    EVENT_TYPE_SALES_ORDER_CREATED,
    EVENT_TYPE_SALES_ORDER_DELETED,
    EVENT_TYPE_SALES_ORDER_UPDATED,
)


class OrderItem(BaseModel):
    """Order line item representation."""

    id: int | None = Field(default=None, description="Item ID")
    name: str = Field(description="Product/Item name")
    product_id: int = Field(description="Product ID")
    variation_id: int | None = Field(default=None, description="Variation ID")
    quantity: int = Field(default=1, description="Quantity ordered")
    tax_class: str | None = Field(default=None, description="Tax class")
    subtotal: str | None = Field(default=None, description="Line subtotal before taxes")
    subtotal_tax: str | None = Field(default=None, description="Line subtotal tax")
    total: str | None = Field(default=None, description="Line total")
    total_tax: str | None = Field(default=None, description="Line total tax")
    sku: str | None = Field(default=None, description="Product SKU")
    price: float | None = Field(default=None, description="Product price")


class OrderBilling(BaseModel):
    """Order billing address and contact information."""

    first_name: str | None = Field(default=None, description="First name")
    last_name: str | None = Field(default=None, description="Last name")
    company: str | None = Field(default=None, description="Company name")
    address_1: str | None = Field(default=None, description="Street address 1")
    address_2: str | None = Field(default=None, description="Street address 2")
    city: str | None = Field(default=None, description="City")
    state: str | None = Field(default=None, description="State / Province")
    postcode: str | None = Field(default=None, description="Postal / Zip code")
    country: str | None = Field(default=None, description="Country code (ISO)")
    email: str | None = Field(default=None, description="Customer email")
    phone: str | None = Field(default=None, description="Customer phone")


class OrderShipping(BaseModel):
    """Order shipping recipient and destination."""

    first_name: str | None = Field(default=None, description="First name")
    last_name: str | None = Field(default=None, description="Last name")
    company: str | None = Field(default=None, description="Company")
    address_1: str | None = Field(default=None, description="Address line 1")
    address_2: str | None = Field(default=None, description="Address line 2")
    city: str | None = Field(default=None, description="City")
    state: str | None = Field(default=None, description="State")
    postcode: str | None = Field(default=None, description="Postcode")
    country: str | None = Field(default=None, description="Country code")


class OrderTaxLine(BaseModel):
    """Order tax breakdown line."""

    id: int | None = Field(default=None, description="Tax line ID")
    rate_code: str | None = Field(default=None, description="Tax rate code")
    rate_id: int | None = Field(default=None, description="Tax rate ID")
    label: str | None = Field(default=None, description="Tax label")
    compound: bool = Field(default=False, description="Is compound tax")
    tax_total: str | None = Field(default=None, description="Tax amount")
    shipping_tax_total: str | None = Field(
        default=None, description="Shipping tax amount"
    )


class Order(EventData):
    """1:1 WooCommerce REST API Order Model."""

    id: int | None = Field(default=None, description="Order ID")
    parent_id: int | None = Field(default=None, description="Parent order ID")
    number: str | None = Field(default=None, description="Order number")
    order_key: str | None = Field(default=None, description="Order key")
    status: str = Field(
        default="pending",
        description="Order status (pending, processing, on-hold, completed, cancelled, refunded, failed)",
    )
    currency: str = Field(default="USD", description="Order currency code")
    date_created: str | None = Field(default=None, description="Date order created")
    date_modified: str | None = Field(default=None, description="Date order modified")
    discount_total: str | None = Field(default=None, description="Total discount")
    discount_tax: str | None = Field(default=None, description="Total discount tax")
    shipping_total: str | None = Field(default=None, description="Total shipping")
    shipping_tax: str | None = Field(default=None, description="Shipping tax")
    cart_tax: str | None = Field(default=None, description="Cart tax")
    total: str | None = Field(default=None, description="Grand total")
    total_tax: str | None = Field(default=None, description="Grand total tax")
    customer_id: int | None = Field(default=None, description="Customer user ID")
    billing: OrderBilling | None = Field(default=None, description="Billing details")
    shipping: OrderShipping | None = Field(default=None, description="Shipping details")
    payment_method: str | None = Field(default=None, description="Payment gateway ID")
    payment_method_title: str | None = Field(
        default=None, description="Payment gateway title"
    )
    transaction_id: str | None = Field(
        default=None, description="Payment transaction ID"
    )
    line_items: list[OrderItem] = Field(
        default_factory=list, description="List of ordered items"
    )
    tax_lines: list[OrderTaxLine] = Field(default_factory=list, description="Tax lines")


class OrderCreated(EventBaseModel):
    """CloudEvent emitted when a customer order is placed."""

    type: str = Field(
        default=EVENT_TYPE_SALES_ORDER_CREATED, description="CloudEvents type"
    )
    source: str = Field(
        default="woocommerce://1/orders", description="Context URI reference"
    )
    subject: str = Field(default="1", description="Numeric site identifier")
    time: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Event timestamp",
    )
    tenant_id: int | str = Field(
        default="default", description="Dedicated tenant extension attribute"
    )
    data: Order = Field(description="Order data payload")


class OrderUpdated(EventBaseModel):
    """CloudEvent emitted when an order status or details are updated."""

    type: str = Field(
        default=EVENT_TYPE_SALES_ORDER_UPDATED, description="CloudEvents type"
    )
    source: str = Field(
        default="woocommerce://1/orders", description="Context URI reference"
    )
    subject: str = Field(default="1", description="Numeric site identifier")
    time: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Event timestamp",
    )
    tenant_id: int | str = Field(
        default="default", description="Dedicated tenant extension attribute"
    )
    data: Order = Field(description="Order data payload")


class OrderCancelled(EventBaseModel):
    """CloudEvent emitted when an order is cancelled."""

    type: str = Field(
        default=EVENT_TYPE_SALES_ORDER_DELETED, description="CloudEvents type"
    )
    source: str = Field(
        default="woocommerce://1/orders", description="Context URI reference"
    )
    subject: str = Field(default="1", description="Numeric site identifier")
    time: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Event timestamp",
    )
    tenant_id: int | str = Field(
        default="default", description="Dedicated tenant extension attribute"
    )
    data: Order = Field(description="Order data payload")


SalesOrder = Order

__all__ = [
    "Order",
    "OrderBilling",
    "OrderCancelled",
    "OrderCreated",
    "OrderItem",
    "OrderShipping",
    "OrderTaxLine",
    "OrderUpdated",
    "SalesOrder",
]
