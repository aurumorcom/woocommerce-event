"""Unit tests for Windmill repository adapters."""

import os

import pytest
from woocommerce_event.repositories.windmill import (
    WindmillCredentialsRepository,
    WindmillStateRepository,
)


@pytest.mark.asyncio
async def test_windmill_credentials_env_fallback():
    """Test environment variable fallback for WindmillCredentialsRepository."""
    repo = WindmillCredentialsRepository()
    os.environ["WOOCOMMERCE_SITE_URL"] = "https://env.example.com"
    os.environ["WOOCOMMERCE_CONSUMER_KEY"] = "ck_env"
    os.environ["WOOCOMMERCE_CONSUMER_SECRET"] = "cs_env"

    creds = await repo.get_credentials(1, 101)
    assert creds.site_url == "https://env.example.com"
    assert creds.consumer_key == "ck_env"
    assert creds.consumer_secret == "cs_env"

    del os.environ["WOOCOMMERCE_SITE_URL"]
    del os.environ["WOOCOMMERCE_CONSUMER_KEY"]
    del os.environ["WOOCOMMERCE_CONSUMER_SECRET"]


@pytest.mark.asyncio
async def test_windmill_state_local_cache():
    """Test state caching in WindmillStateRepository."""
    repo = WindmillStateRepository()
    await repo.set_state("test_token", "abc123xyz")
    val = await repo.get_state("test_token")
    assert val == "abc123xyz"
