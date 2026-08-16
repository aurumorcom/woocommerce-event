"""Unit tests for order schemas."""

from fixtures.woocommerce_api_samples import SAMPLE_ORDER_RAW
from woocommerce_event.modules.orders.schemas import Order, OrderCreated


def test_order_model_validation():
    """Test validating sample WooCommerce order."""
    order = Order.model_validate(SAMPLE_ORDER_RAW)
    assert order.id == 1001
    assert order.total == "37.99"
    assert order.status == "processing"
    assert len(order.line_items) == 1
    assert order.line_items[0].product_id == 799
    assert order.billing is not None
    assert order.billing.first_name == "Jane"


def test_order_created_cloudevent():
    """Test OrderCreated CloudEvent schema."""
    order = Order.model_validate(SAMPLE_ORDER_RAW)
    event = OrderCreated(
        id="evt-ord-1",
        source="woocommerce://101/orders",
        subject="101",
        tenant_id=1,
        data=order,
    )
    assert event.type == "sales-order.created"
    assert event.subject == "101"
    assert event.tenant_id == 1
    assert event.data.id == 1001
