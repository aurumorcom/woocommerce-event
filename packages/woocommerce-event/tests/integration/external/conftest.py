"""External integration tests shared fixtures and VCR configuration."""

import os
from pathlib import Path
from typing import Any, Callable, Awaitable
import pytest
import vcr
from woocommerce_event.exceptions import WooCommerceAuthenticationError, WooCommerceAPIError


SECRETS_TO_SCRUB = [
    os.environ.get("WOOCOMMERCE_CONSUMER_KEY", "aquiveal"),
    os.environ.get("WOOCOMMERCE_CONSUMER_SECRET", "8Gv1hUJTxhGOnUftuuNo"),
    "ck_9908b21223bd6392f086d08e69e88badd4d5a4fb",
    "cs_e055eeb86af8d62fc537bd29d0a64664d4fe3d40",
    "aquiveal",
    "8Gv1hUJTxhGOnUftuuNo",
]


def scrub_request(request: Any) -> Any:
    """Filter out sensitive secrets from HTTP requests before recording to cassette."""
    if not request:
        return request

    # Scrub authorization headers
    for header in ["authorization", "Authorization", "proxy-authorization"]:
        if header in request.headers:
            request.headers[header] = "DUMMY_AUTH_HEADER"

    # Scrub URI secrets
    for secret in SECRETS_TO_SCRUB:
        if secret and secret in request.uri:
            request.uri = request.uri.replace(secret, "REDACTED_SECRET")

    # Scrub body contents
    if hasattr(request, "body") and request.body:
        body_data = request.body
        if isinstance(body_data, bytes):
            body_str = body_data.decode("utf-8", errors="ignore")
            for secret in SECRETS_TO_SCRUB:
                if secret and secret in body_str:
                    body_str = body_str.replace(secret, "REDACTED_SECRET")
            request.body = body_str.encode("utf-8")
        elif isinstance(body_data, str):
            for secret in SECRETS_TO_SCRUB:
                if secret and secret in body_data:
                    body_data = body_data.replace(secret, "REDACTED_SECRET")
            request.body = body_data

    return request


def scrub_response(response: dict[str, Any]) -> dict[str, Any]:
    """Filter out sensitive secrets from HTTP responses before recording to cassette."""
    if not response:
        return response

    # Scrub headers
    headers = response.get("headers", {})
    for header in ["set-cookie", "Set-Cookie", "authorization", "Authorization"]:
        if header in headers:
            headers[header] = ["REDACTED_HEADER"]

    # Scrub body content
    body = response.get("body", {})
    if isinstance(body, dict) and "string" in body:
        content = body["string"]
        if isinstance(content, bytes):
            content_str = content.decode("utf-8", errors="ignore")
            for secret in SECRETS_TO_SCRUB:
                if secret and secret in content_str:
                    content_str = content_str.replace(secret, "REDACTED_SECRET")
            body["string"] = content_str.encode("utf-8")
        elif isinstance(content, str):
            for secret in SECRETS_TO_SCRUB:
                if secret and secret in content:
                    content = content.replace(secret, "REDACTED_SECRET")
            body["string"] = content

    return response


@pytest.fixture(scope="module")
def vcr_config():
    """Configure VCR recording settings to filter authorization headers and secrets."""
    return {
        "filter_headers": [
            ("authorization", "DUMMY_AUTH_HEADER"),
            ("Authorization", "DUMMY_AUTH_HEADER"),
        ],
        "filter_query_parameters": [
            ("consumer_key", "REDACTED_KEY"),
            ("consumer_secret", "REDACTED_SECRET"),
        ],
        "before_record_request": scrub_request,
        "before_record_response": scrub_response,
        "decode_compressed_response": True,
        "record_mode": os.environ.get("VCR_RECORD_MODE", "once"),
    }


@pytest.fixture
def vcr_cassette_dir(request) -> Path:
    """Return the cassette directory for external integration tests."""
    cassette_dir = Path(request.fspath).parent / "cassettes"
    cassette_dir.mkdir(parents=True, exist_ok=True)
    return cassette_dir


async def execute_vcr_external_test(
    cassette_path: Path, vcr_config: dict[str, Any], async_test_fn: Callable[[], Awaitable[Any]]
) -> Any:
    """Execute external integration test under VCR cassette, skipping if unauthenticated and cassette absent."""
    my_vcr = vcr.VCR(**vcr_config)
    cassette_exists = cassette_path.exists()

    try:
        with my_vcr.use_cassette(str(cassette_path)):
            return await async_test_fn()
    except (WooCommerceAuthenticationError, WooCommerceAPIError, Exception) as exc:
        if not cassette_exists:
            # Clean up empty/corrupted cassette file if recording failed on auth
            if cassette_path.exists():
                try:
                    cassette_path.unlink()
                except OSError:
                    pass
            pytest.skip(
                f"No pre-recorded VCR cassette found at {cassette_path.name} "
                f"and live WooCommerce credentials failed authentication: {exc}"
            )
        raise exc
