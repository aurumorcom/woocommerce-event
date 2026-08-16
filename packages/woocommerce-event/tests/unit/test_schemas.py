"""Unit tests for root schemas (Credentials, Site)."""

from woocommerce_event.schemas import Credentials, Site


def test_credentials_schema():
    """Test instantiation and validation of Credentials model."""
    creds = Credentials(
        site_url="https://example.com",
        consumer_key="ck_123",
        consumer_secret="cs_456",
    )
    assert creds.site_url == "https://example.com"
    assert creds.consumer_key == "ck_123"
    assert creds.consumer_secret == "cs_456"


def test_site_context_schema():
    """Test instantiation and validation of Site model."""
    ctx = Site(tenant_id=1, site_id=101, environment="staging")
    assert ctx.tenant_id == 1
    assert ctx.site_id == 101
    assert ctx.environment == "staging"

    # Test channel_id alias support
    ctx_alias = Site.model_validate(
        {"tenantId": 2, "channel_id": 202, "environment": "production"}
    )
    assert ctx_alias.tenant_id == 2
    assert ctx_alias.site_id == 202
