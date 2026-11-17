---
sidebar_position: 1
---

# Install the Agent Skill

The Agent Skill lets an AI assistant look up Greek supermarket prices on its own. It is a folder with a `SKILL.md` that tells the assistant how to reason, and a small Python script that fetches and filters the data. It does not need the REST API to be running.

## Prerequisites

- [uv](https://docs.astral.sh/uv/) - runs the script and installs its dependencies on first use
- Internet access, to fetch the public price data

## Install

The skill lives in [`skills/greek-supermarket/`](https://github.com/kostantinostheo/greek-supermarket/tree/main/skills/greek-supermarket). Copy or symlink that folder into your skills directory.

### Claude Code

For all projects:

```bash
ln -s /path/to/greek-supermarket/skills/greek-supermarket ~/.claude/skills/greek-supermarket
```

For a single project, use `.claude/skills/` inside that project instead.

Once installed, the skill activates when you ask about supermarket products, prices, or shopping lists.

### Other agents

Any agent that supports the [Agent Skills](https://agentskills.io) format can use the same folder. The agent needs to be able to run shell commands and reach the internet.

## Commands

The assistant calls one script. You can also run it yourself:

```bash
cd skills/greek-supermarket
uv run scripts/supermarket.py search "γαλα δελτα"
```

| Command                          | Description                                                           |
|----------------------------------|-----------------------------------------------------------------------|
| `search "<words>"`               | Find products by name (accent and case insensitive, all words match)  |
| `category "<name>"`              | Products in a category                                                |
| `merchant "<name>"`              | Products sold by a merchant, with that merchant's price               |
| `categories`                     | List category names                                                   |
| `merchants`                      | List merchant names                                                   |
| `count`                          | Total number of products                                              |

Useful options for `search`, `category` and `merchant`:

| Option              | Description                                      |
|---------------------|--------------------------------------------------|
| `--limit N`         | Maximum products to print (default 25)           |
| `--sort price\|name`| Cheapest first (default) or alphabetical         |
| `--json`            | Print raw JSON instead of compact lines          |
| `--grep "<words>"`  | Filter by name (`category` and `merchant` only)  |
| `--category`, `--merchant` | Narrow a `search` (`search` only)         |

Put `--refresh` before the command to ignore the cache.

## Caching

Data is cached on disk for 60 minutes in `~/.cache/greek-supermarket/data.json` (or `$XDG_CACHE_HOME`). Delete the file or pass `--refresh` to force a new download.
