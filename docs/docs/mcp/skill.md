---
sidebar_position: 2
---

# Claude Code Skill

The project includes a **Claude Code skill file** (`greek-supermarket-skill.md`) that enhances how AI assistants interact with the MCP server. Instead of calling tools blindly, the skill teaches the assistant to reason about your request, clarify ambiguities, and format results professionally.

## What it does

- **Smart clarification** - If you ask for something broad like "chicken" or "soap", the assistant will ask which sub-type you mean before fetching data
- **Optimized tool sequencing** - Fetches categories first, then drills into the right one, avoiding unnecessary API calls
- **Shopping list mode** - Compare prices across merchants and find the cheapest store for your basket
- **Formatted output** - Results are presented as clean, sorted tables with the lowest price highlighted
- **Language detection** - Responds in Greek or English based on your input
- **Export options** - Get results as a table in chat, Markdown, text, or PDF

## Installation

Copy the skill file to your Claude Code configuration:

```bash
cp greek-supermarket-skill.md ~/.claude/skills/
```

Or symlink it:

```bash
ln -s /path/to/marketgr/greek-supermarket-skill.md ~/.claude/skills/
```

Once installed, the skill activates automatically when you ask about supermarket products, prices, or shopping lists.

## Example queries

```
Find me the cheapest olive oil
```

```
Σύγκρινε τιμές για γάλα σε όλα τα σούπερ μάρκετ
```

```
Build me a shopping list: chicken, rice, tomatoes, dish soap
```

```
What does Sklavenitis sell?
```

## How it works

The skill follows a 4-step process:

1. **Reason** - Analyze the request, check for ambiguity, decide which tools to call
2. **Fetch** - Call MCP tools in the right order (categories → products → filter)
3. **Format** - Build a professional comparison table sorted by price
4. **Present** - Show results in the user's language with export options

:::tip
The skill works best with [Claude Code](https://claude.com/claude-code) but the MCP server itself is compatible with any MCP client.
:::
