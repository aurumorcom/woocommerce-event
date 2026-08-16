import json
from pathlib import Path
from typing import Any

import structlog

from scripts.analyze_woocommerce_fields import (
    classify_fields,
    extract_properties_from_schema,
)

logger = structlog.get_logger(__name__)

TYPE_MAPPING = {
    "string": "str",
    "integer": "int",
    "number": "float",
    "boolean": "bool",
    "array": "list[Any]",
    "object": "dict[str, Any]",
    "mixed": "Any",
}


def pythonize_name(name: str) -> str:
    """Convert schema field names to valid Python identifier in snake_case."""
    reserved_words = {
        "from",
        "import",
        "class",
        "def",
        "global",
        "pass",
        "return",
        "type",
        "id",
    }
    safe_name = name.replace("-", "_")
    if safe_name in reserved_words:
        return f"{safe_name}_val"
    return safe_name


def generate_pydantic_code_for_schema(
    model_name: str, properties: dict[str, Any]
) -> str:
    """Generate Python source code for Pydantic BaseModel from schema properties."""
    classification = classify_fields(properties)
    core = classification["core_fields"]
    computed = classification["computed_fields"]

    lines = [
        "from typing import Any",
        "from pydantic import BaseModel, Field, computed_field",
        "",
        "",
        f"class {model_name}(BaseModel):",
        f'    """1:1 Generated Pydantic representation for WooCommerce {model_name}."""',
    ]

    if not properties:
        lines.append("    pass")
        return "\n".join(lines)

    for prop_name, meta in core.items():
        py_name = pythonize_name(prop_name)
        type_str = TYPE_MAPPING.get(meta["type"], "Any")
        desc = meta.get("description", "").replace('"', '\\"')
        default = meta.get("default")

        field_args = [f'description="{desc}"'] if desc else []
        if prop_name != py_name:
            field_args.append(f'alias="{prop_name}"')

        if default is not None:
            if isinstance(default, str):
                field_args.insert(0, f'default="{default}"')
            else:
                field_args.insert(0, f"default={default}")
            line = f"    {py_name}: {type_str} = Field({', '.join(field_args)})"
        elif not meta.get("required", False):
            field_args.insert(0, "default=None")
            line = f"    {py_name}: {type_str} | None = Field({', '.join(field_args)})"
        else:
            line = f"    {py_name}: {type_str} = Field({', '.join(field_args)})"

        lines.append(line)

    for prop_name, meta in computed.items():
        py_name = pythonize_name(prop_name)
        type_str = TYPE_MAPPING.get(meta["type"], "Any")
        desc = meta.get("description", "").replace('"', '\\"')
        field_args = (
            [f'description="Computed/Read-only: {desc}"']
            if desc
            else ['description="Computed/Read-only field"']
        )
        if prop_name != py_name:
            field_args.append(f'alias="{prop_name}"')
        field_args.insert(0, "default=None")
        line = f"    {py_name}: {type_str} | None = Field({', '.join(field_args)})"
        lines.append(line)

    lines.append("")
    return "\n".join(lines)


def generate_models_from_json(json_path: Path) -> str:
    """Generate model code from a JSON Schema file."""
    logger.debug("Generating Pydantic models from JSON file", path=str(json_path))
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    model_name = "".join(
        part.capitalize() for part in json_path.stem.lower().split("_")
    )
    props = extract_properties_from_schema(data)
    code = generate_pydantic_code_for_schema(model_name, props)
    logger.info(
        "Successfully generated Pydantic code",
        model_name=model_name,
        properties_count=len(props),
    )
    return code


if __name__ == "__main__":
    data_dir = Path(__file__).resolve().parent.parent / "data"
    for json_file in data_dir.glob("*.json"):
        code = generate_models_from_json(json_file)
        print(f"# Model: {json_file.stem}\n{code[:300]}...\n")
