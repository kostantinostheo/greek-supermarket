---
sidebar_position: 1
slug: /intro
---

# Introduction

**Greek Supermarket** is an open-source project that provides price transparency for Greek supermarket products. It aggregates publicly available pricing data and exposes it through a clean REST API and an Agent Skill for AI assistants.

## Architecture

![Architecture Overview](/img/architecture.svg)

## What's included

- **REST API** - FastAPI server with endpoints for products, categories, merchants, and search
- **Agent Skill** - Lets AI assistants (Claude Code and other skill-compatible agents) look up and compare Greek supermarket prices

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/kostantinostheo/greek-supermarket.git
cd greek-supermarket
```

### 2. Use the Agent Skill

Link the skill into your agent's skills folder (requires [uv](https://docs.astral.sh/uv/)):

```bash
ln -s "$(pwd)/skills/greek-supermarket" ~/.claude/skills/greek-supermarket
```

See [Install the Agent Skill](./skill/install) for details and the available commands.

### 3. Run the REST API (optional)

The API is a Python app managed with uv:

```bash
cd api
uv sync
uv run server.py
```

The API runs on `http://localhost:8000` by default. Interactive API documentation (Swagger UI) is available at [http://localhost:8000/api-docs](http://localhost:8000/api-docs).

## Data Source

Product and pricing data is aggregated from publicly available sources and refreshed every 60 minutes.
