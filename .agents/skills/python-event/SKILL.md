---
name: python-event
description: Provides specialized context, rules, and tools for implementing, configuring, and debugging python-event. Use this skill whenever modifying python-event configurations or adding related functionality.
---
# python-event

## File Tree

```text
python-event/
├── assets
├── modules
│   └── python-event (http://github.com/aurumorinc/python-even)
├── references
├── scripts
└── SKILL.md
```

> **Agent Instructions:** The `modules/` directory contains full source code repositories. Probe is configured for this workspace. Use Probe MCP tools to inspect and search code dynamically across target folder paths instead of raw static AST dumps:
> - `probe search "<query>" [path]` - Search code semantically with Elasticsearch-style syntax.
> - `probe extract <file>:<line>` - Extract complete AST semantic blocks.
> - `probe query "<pattern>"` - Perform AST structural pattern matching.
> - `probe symbols <file>` - List code symbols (functions, classes, constants) in target file.