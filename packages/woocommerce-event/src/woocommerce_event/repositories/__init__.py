"""Repositories package for credentials and state caching."""

__ignore__ = ["logger"]
from woocommerce_event.repositories import memory, windmill
from woocommerce_event.repositories.memory import (
    MemoryCredentialsRepository,
    MemoryStateRepository,
)
from woocommerce_event.repositories.windmill import (
    WindmillCredentialsRepository,
    WindmillStateRepository,
)

__all__ = [
    "MemoryCredentialsRepository",
    "MemoryStateRepository",
    "WindmillCredentialsRepository",
    "WindmillStateRepository",
    "memory",
    "windmill",
]
