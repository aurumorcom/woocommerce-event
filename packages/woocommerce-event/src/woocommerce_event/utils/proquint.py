"""Deterministic Proquint (PROnounceable QUINTuplet) encoding utilities."""

import hashlib

CONSONANTS: str = "bdfghjklmnprstvz"
VOWELS: str = "aiou"


def uint16_to_proquint(val: int) -> str:
    """Convert a 16-bit unsigned integer (0..65535) into a 5-letter proquint syllable."""
    v = val & 0xFFFF
    c1 = CONSONANTS[(v >> 12) & 0x0F]
    v1 = VOWELS[(v >> 10) & 0x03]
    c2 = CONSONANTS[(v >> 6) & 0x0F]
    v2 = VOWELS[(v >> 4) & 0x03]
    c3 = CONSONANTS[v & 0x0F]
    return f"{c1}{v1}{c2}{v2}{c3}"


def proquint_to_uint16(syllable: str) -> int:
    """Decode a 5-letter proquint syllable back into a 16-bit integer."""
    if len(syllable) != 5:
        raise ValueError(
            f"Proquint syllable must be exactly 5 characters, got '{syllable}'"
        )
    c1 = CONSONANTS.index(syllable[0])
    v1 = VOWELS.index(syllable[1])
    c2 = CONSONANTS.index(syllable[2])
    v2 = VOWELS.index(syllable[3])
    c3 = CONSONANTS.index(syllable[4])
    return (c1 << 12) | (v1 << 10) | (c2 << 6) | (v2 << 4) | c3


def encode_numeric_ids_to_proquint(tenant_id: int | str, site_id: int | str) -> str:
    """Convert numeric tenant_id and site_id into a 2-syllable Proquint slug (e.g. lusab_babad)."""
    try:
        t_id = int(tenant_id)
        s_id = int(site_id)
    except ValueError:
        # If non-numeric strings are passed, hash them deterministically
        raw_key = f"{tenant_id}:{site_id}".encode()
        digest = hashlib.sha256(raw_key).digest()
        quint1 = uint16_to_proquint(int.from_bytes(digest[0:2], byteorder="big"))
        quint2 = uint16_to_proquint(int.from_bytes(digest[2:4], byteorder="big"))
        return f"{quint1}_{quint2}"

    if 0 <= t_id < 65536 and 0 <= s_id < 65536:
        quint1 = uint16_to_proquint(t_id)
        quint2 = uint16_to_proquint(s_id)
        return f"{quint1}_{quint2}"

    # Fallback to deterministic SHA-256 for numbers >= 65536
    digest = hashlib.sha256(f"{t_id}:{s_id}".encode()).digest()
    quint1 = uint16_to_proquint(int.from_bytes(digest[0:2], byteorder="big"))
    quint2 = uint16_to_proquint(int.from_bytes(digest[2:4], byteorder="big"))
    return f"{quint1}_{quint2}"


def get_proquint_windmill_resource_path(
    tenant_id: int | str, site_id: int | str
) -> str:
    """Generate standardized Windmill resource path: f/woocommerce_event/{proquint_slug}_woocommerce."""
    slug = encode_numeric_ids_to_proquint(tenant_id, site_id)
    return f"f/woocommerce_event/{slug}_woocommerce"


__all__ = [
    "encode_numeric_ids_to_proquint",
    "get_proquint_windmill_resource_path",
    "proquint_to_uint16",
    "uint16_to_proquint",
]
