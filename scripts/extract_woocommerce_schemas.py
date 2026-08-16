import asyncio
import json
import os
from pathlib import Path
from typing import Any

import httpx
import structlog

logger = structlog.get_logger(__name__)

SITE_URL = os.environ.get(
    "WORDPRESS_SITE_URL", "https://abhigaming5z.capybaara.com/"
).rstrip("/")
CONSUMER_KEY = os.environ.get(
    "WOOCOMMERCE_CONSUMER_KEY", "ck_766ba6b1e5e75897bc97d95adef3405b097ce6da"
)
CONSUMER_SECRET = os.environ.get(
    "WOOCOMMERCE_CONSUMER_SECRET", "cs_40765de0ef7407502c98b160e0bae08b84c67c34"
)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

ENDPOINTS = {
    "PRODUCTS.json": "/wp-json/wc/v3/products",
    "ORDERS.json": "/wp-json/wc/v3/orders",
    "CATEGORIES.json": "/wp-json/wc/v3/products/categories",
    "TAGS.json": "/wp-json/wc/v3/products/tags",
    "ATTRIBUTES.json": "/wp-json/wc/v3/products/attributes",
    "MEDIA.json": "/wp-json/wp/v2/media",
    "WEBHOOKS.json": "/wp-json/wc/v3/webhooks",
    "SYSTEM_STATUS.json": "/wp-json/wc/v3/system_status",
}


async def fetch_schema(
    client: httpx.AsyncClient, file_name: str, path: str
) -> dict[str, Any] | None:
    url = f"{SITE_URL}{path}"
    logger.info("Fetching schema via OPTIONS", file_name=file_name, url=url)
    try:
        response = await client.options(
            url,
            auth=(CONSUMER_KEY, CONSUMER_SECRET),
            timeout=30.0,
            follow_redirects=True,
        )
        if response.status_code in (200, 201):
            data = response.json()
            out_file = DATA_DIR / file_name
            out_file.write_text(json.dumps(data, indent=4), encoding="utf-8")
            logger.info(
                "Successfully saved schema",
                file_name=out_file.name,
                bytes=len(response.content),
            )
            return data
        else:
            logger.warning(
                "OPTIONS failed, attempting fallback GET",
                status_code=response.status_code,
                url=url,
            )
            get_resp = await client.get(
                url,
                auth=(CONSUMER_KEY, CONSUMER_SECRET),
                params={"per_page": 1},
                timeout=30.0,
                follow_redirects=True,
            )
            if get_resp.status_code in (200, 201):
                data = get_resp.json()
                out_file = DATA_DIR / file_name
                out_file.write_text(json.dumps(data, indent=4), encoding="utf-8")
                logger.info(
                    "Successfully written fallback GET sample", file_name=out_file.name
                )
                return data
            else:
                logger.error(
                    "Fallback GET request failed",
                    status_code=get_resp.status_code,
                    url=url,
                )
                return None
    except Exception as e:
        logger.exception("Failed to fetch schema", url=url, error=str(e))
        return None


async def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    logger.info("Starting schema extraction", site_url=SITE_URL, data_dir=str(DATA_DIR))

    async with httpx.AsyncClient(verify=False) as client:
        tasks = [
            fetch_schema(client, file_name, path)
            for file_name, path in ENDPOINTS.items()
        ]
        await asyncio.gather(*tasks)

        try:
            prod_resp = await client.get(
                f"{SITE_URL}/wp-json/wc/v3/products",
                auth=(CONSUMER_KEY, CONSUMER_SECRET),
                params={"per_page": 1},
                timeout=30.0,
                follow_redirects=True,
            )
            if prod_resp.status_code == 200 and prod_resp.json():
                sample_id = prod_resp.json()[0]["id"]
                var_path = f"/wp-json/wc/v3/products/{sample_id}/variations"
                await fetch_schema(client, "VARIANTS.json", var_path)
            else:
                await fetch_schema(
                    client, "VARIANTS.json", "/wp-json/wc/v3/products/attributes"
                )
        except Exception as e:  # noqa: BLE001
            logger.warning("Variations schema fetch skipped", error=str(e))


if __name__ == "__main__":
    asyncio.run(main())
