---
sidebar_position: 2
---

# How the Skill Works

The skill teaches the assistant to reason about your request, clarify ambiguities, run the right queries and format results professionally, instead of dumping raw price data.

## What it does

- **Smart clarification** - If you ask for something broad like "chicken" or "soap", the assistant will ask which sub-type you mean before fetching data
- **Targeted lookups** - Searches by product name and returns only the matching products, so large catalogs never flood the conversation
- **Shopping list mode** - Compare prices across merchants and find the cheapest store for your basket
- **Formatted output** - Results are presented as clean, sorted tables with the lowest price highlighted
- **Language detection** - Responds in Greek or English based on your input
- **Export options** - Get results as a table in chat, Markdown, text, or PDF

See [Install the Agent Skill](./install) for setup.

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

1. **Reason** - Analyze the request and check for ambiguity before searching
2. **Fetch** - Run `search` (or `category` / `merchant`) and narrow the results
3. **Format** - Build a professional comparison table sorted by price
4. **Present** - Show results in the user's language with export options

:::tip
The skill is self-contained. If you want to build your own app on the same data, run the [REST API](../api/products) instead.
:::
