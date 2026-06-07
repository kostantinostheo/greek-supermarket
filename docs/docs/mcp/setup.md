---
sidebar_position: 1
---

# MCP Server Setup

The MCP server lets AI assistants query Greek supermarket data directly using the [Model Context Protocol](https://modelcontextprotocol.io/).

## Prerequisites

```bash
cd mcp
pip install -r requirements.txt
```

## Available Tools

| Tool                       | Description                                          |
|----------------------------|------------------------------------------------------|
| `get_all_products`         | Get all products (paginated)                         |
| `get_number_of_products`   | Get the total number of available products           |
| `get_merchants`            | List all merchant names                              |
| `get_categories`           | List all product categories                          |
| `get_products_by_merchant` | Get products sold by a specific merchant             |
| `get_products_by_category` | Get all products within a specific category          |

## Client Configuration

### Claude Desktop

`~/.claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "greek-supermarket": {
      "command": "python3",
      "args": ["/path/to/greek-supermarket/mcp/mcp_server.py"]
    }
  }
}
```

### Claude Code (CLI)

`.claude/settings.json` or `~/.claude/settings.json`

```json
{
  "mcpServers": {
    "greek-supermarket": {
      "command": "python3",
      "args": ["/path/to/greek-supermarket/mcp/mcp_server.py"]
    }
  }
}
```

### Cursor

`.cursor/mcp.json`

```json
{
  "mcpServers": {
    "greek-supermarket": {
      "command": "python3",
      "args": ["/path/to/greek-supermarket/mcp/mcp_server.py"]
    }
  }
}
```

### Windsurf (Codeium)

`~/.codeium/windsurf/mcp_config.json`

```json
{
  "mcpServers": {
    "greek-supermarket": {
      "command": "python3",
      "args": ["/path/to/greek-supermarket/mcp/mcp_server.py"]
    }
  }
}
```

### VS Code (Copilot)

`.vscode/mcp.json`

```json
{
  "servers": {
    "greek-supermarket": {
      "command": "python3",
      "args": ["/path/to/greek-supermarket/mcp/mcp_server.py"]
    }
  }
}
```

### Zed

`~/.config/zed/settings.json` (or via Agent Panel → Settings → "Add Custom Server")

```json
{
  "context_servers": {
    "greek-supermarket": {
      "command": "python3",
      "args": ["/path/to/greek-supermarket/mcp/mcp_server.py"]
    }
  }
}
```

:::tip
Replace `/path/to/greek-supermarket/` with the actual path on your machine. If using a virtual environment, point to that Python binary instead.
:::
