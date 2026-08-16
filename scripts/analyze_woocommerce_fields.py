import json
from pathlib import Path
from typing import Any

import structlog

logger = structlog.get_logger(__name__)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def extract_properties_from_schema(schema_data: dict[str, Any]) -> dict[str, Any]:
    """Extract property definitions from either a JSON Schema root or WooCommerce endpoint schema."""
    if "schema" in schema_data and isinstance(schema_data["schema"], dict):
        props = schema_data["schema"].get("properties", {})
        if props:
            return props
    if "properties" in schema_data and isinstance(schema_data["properties"], dict):
        return schema_data["properties"]
    # Fallback to scanning endpoints POST/PUT args
    if "endpoints" in schema_data and isinstance(schema_data["endpoints"], list):
        for ep in schema_data["endpoints"]:
            if "POST" in ep.get("methods", []) or "PUT" in ep.get("methods", []):
                args = ep.get("args", {})
                if args:
                    return args
    return {}


def classify_fields(properties: dict[str, Any]) -> dict[str, Any]:
    """Classify fields into core input vs computed/read-only with type metadata."""
    core_fields: dict[str, Any] = {}
    computed_fields: dict[str, Any] = {}
    enums: dict[str, list[Any]] = {}

    for prop_name, prop_def in properties.items():
        if not isinstance(prop_def, dict):
            continue

        is_readonly = prop_def.get("readonly", False)
        field_type = prop_def.get("type", "string")
        description = prop_def.get("description", "")
        default_val = prop_def.get("default")
        enum_vals = prop_def.get("enum")

        field_metadata = {
            "type": field_type,
            "description": description,
            "default": default_val,
            "required": prop_def.get("required", False),
        }

        if enum_vals:
            enums[prop_name] = enum_vals
            field_metadata["enum"] = enum_vals

        if is_readonly:
            computed_fields[prop_name] = field_metadata
        else:
            core_fields[prop_name] = field_metadata

    return {
        "core_fields": core_fields,
        "computed_fields": computed_fields,
        "enums": enums,
        "total_properties": len(properties),
    }


def analyze_file(schema_path: Path) -> dict[str, Any]:
    """Analyze a single schema file and return classification statistics."""
    logger.debug("Analyzing WooCommerce schema file", path=str(schema_path))
    with open(schema_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    props = extract_properties_from_schema(data)
    classification = classify_fields(props)
    logger.info(
        "Schema field analysis completed",
        schema_file=schema_path.name,
        core_count=len(classification["core_fields"]),
        computed_count=len(classification["computed_fields"]),
        enum_count=len(classification["enums"]),
    )
    return classification


def analyze_all_schemas(data_dir: Path = DATA_DIR) -> dict[str, Any]:
    """Analyze all JSON files in the data directory."""
    results: dict[str, Any] = {}
    for json_file in data_dir.glob("*.json"):
        results[json_file.stem] = analyze_file(json_file)
    return results


if __name__ == "__main__":
    analysis = analyze_all_schemas()
    print(
        json.dumps(
            {
                k: {
                    "core": len(v["core_fields"]),
                    "computed": len(v["computed_fields"]),
                }
                for k, v in analysis.items()
            },
            indent=2,
        )
    )
