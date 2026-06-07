---
sidebar_position: 1
slug: /intro
---

# Introduction

**Greek Supermarket** is an open-source project that provides price transparency for Greek supermarket products. It aggregates publicly available pricing data and exposes it through a clean REST API and an MCP (Model Context Protocol) server.

## Architecture

![Architecture Overview](/img/architecture.svg)

## What's included

- **REST API** - Express.js server with endpoints for products, categories, merchants, and search
- **MCP Server** - Connect AI assistants (Claude, Cursor, VS Code Copilot, etc.) directly to Greek supermarket data

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/kostantinostheo/greek-supermarket.git
cd greek-supermarket
```

### 2. Start the API

```bash
cd api
npm install
npm start
```

The API runs on `http://localhost:8000` by default. Interactive API documentation (Swagger UI) is available at [http://localhost:8000/api-docs/](http://localhost:8000/api-docs/#/).

### 3. Use the MCP Server

```bash
cd mcp
pip install -r requirements.txt
python3 mcp_server.py
```

See the [MCP Setup guide](./mcp/setup) for connecting it to your AI assistant.

## Data Source

Product and pricing data is aggregated from publicly available sources and refreshed every 60 minutes.
