"""Build tools/anthropic-tools.json from the Klaracase OpenAPI file.

Usage: python3 -I scripts/anthropic-tools.py ../_contract/openapi-v1.json [output.json]

Each customer operation that names an MCP tool (`x-mcp-tool`) becomes one
Anthropic tool_use definition: name, description, input_schema.
"""

import json
import sys
from pathlib import Path

DEFAULT_OUT = Path(__file__).resolve().parent.parent / "tools" / "anthropic-tools.json"
# Arguments the MCP tool does not take. Uploads are not among the nine tools.
SKIPPED = {("check_citations", "document_id")}
# The OpenAPI body marks `text` optional because document_id is its alternative.
FORCED_REQUIRED = {"check_citations": ["text"]}
KEEP = ("type", "enum", "items", "minimum", "maximum", "maxItems", "minItems", "format")


def clean(schema: dict, description: str) -> dict:
    out = {key: schema[key] for key in KEEP if key in schema}
    if "items" in out:
        out["items"] = clean(out["items"], "")
        out["items"].pop("description", None)
    if description:
        out["description"] = description.strip()
    return out


def first_paragraph(text: str, banned: tuple = ()) -> str:
    sentences = " ".join(text.strip().split("\n\n")[0].split()).split(". ")
    return ". ".join(s for s in sentences if not any(word in s for word in banned))


def build_tool(path_item: dict, operation: dict) -> dict:
    name = operation["x-mcp-tool"]
    properties: dict = {}
    required: list = []
    parameters = path_item.get("parameters", []) + operation.get("parameters", [])
    for param in parameters:
        properties[param["name"]] = clean(param["schema"], param.get("description", ""))
        if param.get("required"):
            required.append(param["name"])
    body = operation.get("requestBody", {}).get("content", {}).get("application/json")
    if body:
        schema = body["schema"]
        for prop, sub in schema.get("properties", {}).items():
            properties[prop] = clean(sub, sub.get("description", ""))
        required += schema.get("required", [])
    for tool, prop in SKIPPED:
        if tool == name:
            properties.pop(prop, None)
    required = FORCED_REQUIRED.get(name, required)
    banned = ("document_id", "upload") if any(tool == name for tool, _ in SKIPPED) else ()
    description = operation["summary"].strip() + ". " + first_paragraph(operation["description"], banned)
    return {
        "name": name,
        "description": description,
        "input_schema": {
            "type": "object",
            "properties": properties,
            "required": required,
            "additionalProperties": False,
        },
    }


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    spec = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    tools = []
    for path_item in spec["paths"].values():
        for method, operation in path_item.items():
            if method == "parameters" or "x-mcp-tool" not in operation:
                continue
            tools.append(build_tool(path_item, operation))
    tools.sort(key=lambda tool: tool["name"])
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_OUT
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(tools, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {len(tools)} tools to {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
