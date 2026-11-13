# Legacy code (unsupported)

This folder keeps the previous MCP implementation for reference. It is **not** the
supported entry point and does not run with the pinned dependency set in
`pyproject.toml`.

- `mcp_server.py` — earlier stdio server built on the `mcp` 2.x `MCPServer` API.
  It also disables TLS verification (`verify=False`) on its upstream calls.
- `usage_log.py` — local JSONL call counter used by that server.
- `sina_stock_api.py`, `qq_stock_api.py` — Sina/Tencent quote helpers it imports.

The supported implementation lives in `qinglong/` and is installed as the
`qinglong-mcp` command. See the top-level `README.md`.

If you want to run this legacy server instead, install it in its own environment
with `mcp>=2`:

```bash
python -m venv .venv-legacy && source .venv-legacy/bin/activate
pip install "mcp>=2" requests
python legacy/mcp_server.py
```
