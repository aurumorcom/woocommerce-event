"""Unit tests for centralized canonical Kafka topics and CloudEvents event types."""

from woocommerce_event.constants import (
    EVENT_TYPE_CHANNEL_CREATED,
    EVENT_TYPE_CHANNEL_DELETED,
    EVENT_TYPE_CHANNEL_UPDATED,
    EVENT_TYPE_ITEM_ATTRIBUTE_CREATED,
    EVENT_TYPE_ITEM_ATTRIBUTE_DELETED,
    EVENT_TYPE_ITEM_ATTRIBUTE_UPDATED,
    EVENT_TYPE_ITEM_ATTRIBUTE_VALUE_CREATED,
    EVENT_TYPE_ITEM_ATTRIBUTE_VALUE_DELETED,
    EVENT_TYPE_ITEM_ATTRIBUTE_VALUE_UPDATED,
    EVENT_TYPE_ITEM_CATEGORY_CREATED,
    EVENT_TYPE_ITEM_CATEGORY_DELETED,
    EVENT_TYPE_ITEM_CATEGORY_UPDATED,
    EVENT_TYPE_ITEM_CREATED,
    EVENT_TYPE_ITEM_DELETED,
    EVENT_TYPE_ITEM_PRICE_CREATED,
    EVENT_TYPE_ITEM_PRICE_DELETED,
    EVENT_TYPE_ITEM_PRICE_UPDATED,
    EVENT_TYPE_ITEM_TAG_CREATED,
    EVENT_TYPE_ITEM_TAG_DELETED,
    EVENT_TYPE_ITEM_TAG_UPDATED,
    EVENT_TYPE_ITEM_UPDATED,
    EVENT_TYPE_MEDIA_CREATED,
    EVENT_TYPE_MEDIA_DELETED,
    EVENT_TYPE_MEDIA_UPDATED,
    EVENT_TYPE_PRODUCT_CREATED,
    EVENT_TYPE_PRODUCT_DELETED,
    EVENT_TYPE_PRODUCT_UPDATED,
    EVENT_TYPE_PRODUCT_VARIANT_CREATED,
    EVENT_TYPE_PRODUCT_VARIANT_DELETED,
    EVENT_TYPE_PRODUCT_VARIANT_UPDATED,
    EVENT_TYPE_SALES_ORDER_CREATED,
    EVENT_TYPE_SALES_ORDER_DELETED,
    EVENT_TYPE_SALES_ORDER_UPDATED,
    EVENT_TYPE_STOCK_LEVEL_CREATED,
    EVENT_TYPE_STOCK_LEVEL_DELETED,
    EVENT_TYPE_STOCK_LEVEL_UPDATED,
    TOPIC_CHANNEL,
    TOPIC_ITEM,
    TOPIC_ITEM_ATTRIBUTE,
    TOPIC_ITEM_ATTRIBUTE_VALUE,
    TOPIC_ITEM_CATEGORY,
    TOPIC_ITEM_PRICE,
    TOPIC_ITEM_TAG,
    TOPIC_MEDIA,
    TOPIC_PRODUCT,
    TOPIC_PRODUCT_VARIANT,
    TOPIC_SALES_ORDER,
    TOPIC_STOCK_LEVEL,
    TOPICS,
)


def test_topics_set_contains_exact_12_canonical_topics() -> None:
    """Verify TOPICS contains exactly the 12 specified canonical topics without prefixes."""
    expected_topics = {
        "product",
        "product-variant",
        "sales-order",
        "item-tag",
        "item",
        "item-attribute",
        "item-attribute-value",
        "item-category",
        "item-price",
        "channel",
        "stock-level",
        "media",
    }
    assert TOPICS == expected_topics
    assert len(TOPICS) == 12


def test_no_topics_contain_woocommerce_prefix() -> None:
    """Verify that zero topics start with woocommerce. or contain vendor prefixes."""
    for topic in TOPICS:
        assert not topic.startswith("woocommerce.")
        assert not topic.endswith(".events")
        assert topic == topic.lower()


def test_individual_topic_constants() -> None:
    """Verify each individual topic constant matches expected value."""
    assert TOPIC_PRODUCT == "product"
    assert TOPIC_PRODUCT_VARIANT == "product-variant"
    assert TOPIC_SALES_ORDER == "sales-order"
    assert TOPIC_ITEM_TAG == "item-tag"
    assert TOPIC_ITEM == "item"
    assert TOPIC_ITEM_ATTRIBUTE == "item-attribute"
    assert TOPIC_ITEM_ATTRIBUTE_VALUE == "item-attribute-value"
    assert TOPIC_ITEM_CATEGORY == "item-category"
    assert TOPIC_ITEM_PRICE == "item-price"
    assert TOPIC_CHANNEL == "channel"
    assert TOPIC_STOCK_LEVEL == "stock-level"
    assert TOPIC_MEDIA == "media"


def test_channel_event_type_constants() -> None:
    """Verify channel event types follow channel.created/updated/deleted pattern."""
    assert EVENT_TYPE_CHANNEL_CREATED == "channel.created"
    assert EVENT_TYPE_CHANNEL_UPDATED == "channel.updated"
    assert EVENT_TYPE_CHANNEL_DELETED == "channel.deleted"


def test_attribute_event_type_constants() -> None:
    """Verify attribute and attribute-value event types."""
    assert EVENT_TYPE_ITEM_ATTRIBUTE_CREATED == "item-attribute.created"
    assert EVENT_TYPE_ITEM_ATTRIBUTE_UPDATED == "item-attribute.updated"
    assert EVENT_TYPE_ITEM_ATTRIBUTE_DELETED == "item-attribute.deleted"
    assert EVENT_TYPE_ITEM_ATTRIBUTE_VALUE_CREATED == "item-attribute-value.created"
    assert EVENT_TYPE_ITEM_ATTRIBUTE_VALUE_UPDATED == "item-attribute-value.updated"
    assert EVENT_TYPE_ITEM_ATTRIBUTE_VALUE_DELETED == "item-attribute-value.deleted"


def test_domain_event_type_constants() -> None:
    """Verify domain event types follow canonical pattern."""
    assert EVENT_TYPE_PRODUCT_CREATED == "product.created"
    assert EVENT_TYPE_PRODUCT_UPDATED == "product.updated"
    assert EVENT_TYPE_PRODUCT_DELETED == "product.deleted"
    assert EVENT_TYPE_PRODUCT_VARIANT_CREATED == "product-variant.created"
    assert EVENT_TYPE_PRODUCT_VARIANT_UPDATED == "product-variant.updated"
    assert EVENT_TYPE_PRODUCT_VARIANT_DELETED == "product-variant.deleted"
    assert EVENT_TYPE_SALES_ORDER_CREATED == "sales-order.created"
    assert EVENT_TYPE_SALES_ORDER_UPDATED == "sales-order.updated"
    assert EVENT_TYPE_SALES_ORDER_DELETED == "sales-order.deleted"
    assert EVENT_TYPE_ITEM_TAG_CREATED == "item-tag.created"
    assert EVENT_TYPE_ITEM_TAG_UPDATED == "item-tag.updated"
    assert EVENT_TYPE_ITEM_TAG_DELETED == "item-tag.deleted"
    assert EVENT_TYPE_ITEM_CREATED == "item.created"
    assert EVENT_TYPE_ITEM_UPDATED == "item.updated"
    assert EVENT_TYPE_ITEM_DELETED == "item.deleted"
    assert EVENT_TYPE_ITEM_CATEGORY_CREATED == "item-category.created"
    assert EVENT_TYPE_ITEM_CATEGORY_UPDATED == "item-category.updated"
    assert EVENT_TYPE_ITEM_CATEGORY_DELETED == "item-category.deleted"
    assert EVENT_TYPE_ITEM_PRICE_CREATED == "item-price.created"
    assert EVENT_TYPE_ITEM_PRICE_UPDATED == "item-price.updated"
    assert EVENT_TYPE_ITEM_PRICE_DELETED == "item-price.deleted"
    assert EVENT_TYPE_STOCK_LEVEL_CREATED == "stock-level.created"
    assert EVENT_TYPE_STOCK_LEVEL_UPDATED == "stock-level.updated"
    assert EVENT_TYPE_STOCK_LEVEL_DELETED == "stock-level.deleted"
    assert EVENT_TYPE_MEDIA_CREATED == "media.created"
    assert EVENT_TYPE_MEDIA_UPDATED == "media.updated"
    assert EVENT_TYPE_MEDIA_DELETED == "media.deleted"
