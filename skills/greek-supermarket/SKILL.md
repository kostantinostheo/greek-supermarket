---
name: greek-supermarket
description: "Use this skill for ANY query about Greek supermarket products or prices. Covers product search, price comparison, shopping list optimization, merchant lookup, and category browsing. Trigger on phrases like: \"find me\", \"cheapest\", \"supermarket\", \"price of\", \"compare prices\", \"shopping list\", \"καλάθι\", \"τιμή\", \"φθηνότερο\", \"σούπερ μάρκετ\", \"προϊόν\", \"κατάστημα\", or any request involving food, household, or personal care products across Greek supermarkets. Always use this skill before looking up prices — it governs reasoning, clarification, command sequencing, and output formatting."
compatibility: Requires uv (https://docs.astral.sh/uv/) and internet access.
---

# Greek Supermarket Skill

Live prices for ~2,800 products across Greek supermarkets (ab, bazaar, efresh, kritikos, marketin, masoutis, mymarket — run `merchants` for the current list). Data is fetched on demand and cached for 60 minutes.

## Available Commands

Run everything through one script, relative to this skill's directory:

```bash
uv run scripts/supermarket.py <command>
```

`uv` installs the script's dependencies on first run. If the working directory is not this skill's directory, use the script's absolute path.

| Command | Purpose |
|---------|---------|
| `search "<words>"` | **Main entry point.** Products whose name contains all the words (accent- and case-insensitive, Greek or Latin). Options: `--category`, `--merchant`, `--limit`, `--sort price\|name`, `--json` |
| `category "<name>" [--grep words]` | Products in one category (exact name from `categories`, matched ignoring case and accents) |
| `merchant "<name>" [--grep words]` | Products sold by one merchant, showing only that merchant's price |
| `categories` | List of the 22 category names |
| `merchants` | List of merchant names |
| `count` | Total product count |

Add `--refresh` before the command (`scripts/supermarket.py --refresh search …`) to bypass the cache.

### Reading the output

Each product is one line, cheapest merchant first:

```
name | category | barcode | merchant €price (€unit-price/unit), merchant €price (…), …
```

- `€price` is the shelf price. `(€x/unit)` is the normalized price per kg or per litre — use it to compare different pack sizes.
- Product names are lowercase and often abbreviated, with pack info like `12/1l` (12 bottles of 1 L). Read them carefully before comparing.
- At most 25 products are printed by default. The last line says how many more exist.

---

## Step 1 — Reasoning Before Running Anything

Before searching, think through what the user actually needs.

### Ambiguity check

Users often ask for things that map to many products. Examples:

- "chicken" → could be whole chicken, breast fillet, thigh, frozen, fresh, by brand
- "soap" → hand soap, dish soap, laundry soap, bar soap, liquid soap
- "coffee" → instant, filter, espresso, capsules, decaf, by brand
- "milk" → full fat, semi, skimmed, plant-based, evaporated, condensed

**If the request is ambiguous**, do NOT search yet. Explain to the user:
- That this product spans multiple sub-types or categories
- What the options are (briefly)
- Ask them to confirm which direction before proceeding

Keep the clarification short. One sentence of explanation + a compact list of options. Do not over-explain.

Example (Greek input):
> Το "κοτόπουλο" υπάρχει σε πολλές μορφές στο σύστημα. Τι ψάχνεις;
> - Ολόκληρο κοτόπουλο (τιμή/κιλό)
> - Στήθος / φιλέτο
> - Μπούτι / μηρός
> - Κατεψυγμένο

Example (English input):
> "Chicken" covers many products here. Which are you looking for?
> - Whole chicken (price/kg)
> - Breast fillet
> - Thigh / drumstick
> - Frozen

### Shopping list logic

When the user asks for a full shopping list or "cheapest total basket":

1. Acknowledge that finding the single cheapest store for a full basket requires comparing per-item prices across merchants.
2. Warn (briefly) that not all merchants carry all products, so a single-store optimum may not always exist.
3. Proceed item by item, one `search` per item.
4. For each item, pick the relevant product(s), then show a comparison table.
5. At the end, produce a **basket summary table** showing: for each item, the cheapest available price and where to buy it. Include a "single best store" recommendation if one store wins on most items.

---

## Step 2 — Command Sequencing

Start with `search`. Product names are Greek (sometimes Latin brand names), so search in the language the product is sold in.

```
1. search "<product words>"     ← main path; add --merchant/--category to narrow
2. Too many results?            ← add words to the query, or --category / --limit
3. No results?                  ← try the Greek name, a shorter word, or a brand name
4. Format output
```

### Searching well
- All words must match, so fewer, more specific words work best: `search "ελαιολαδο εξτρα παρθενο"`.
- Accents and case do not matter: `γάλα`, `γαλα` and `ΓΑΛΑ` are the same.
- Match on a stem if inflections differ, e.g. `ντοματ` finds both `ντομάτες` and `ντομάτα`.
- Never load or paste a huge result into your reply. Narrow with `--grep`, `--category`, `--merchant` or `--limit` instead.

### Category name rules
- Category names for `--category` and `category` are matched ignoring case and accents, but must otherwise be exact. If a name is wrong the script prints the closest names.
- There are only 22 categories and some are very broad, so prefer `search` over browsing a whole category.
- If `categories` was already run in this conversation, reuse the result.

### Merchant lookup
Use `merchant` when:
- The user asks "what does [store] sell?" or "what's available at [store]?"
- You need to verify that a specific merchant carries a product (`search "<words>" --merchant <name>`)
- Building a single-store shopping list

Merchant names are exact and lowercase (`ab`, `masoutis`, …). Run `merchants` if unsure.

---

## Step 3 — Output Formatting

### Language rule
- Detect the language of the user's request.
- Respond in the **same language**. If Greek input → Greek output. If English → English.
- Do not mix languages in the same response unless a product name has no translation.

### Output format options
After completing the research, ask the user (once, briefly):

> How would you like the results?
> - **Table in chat** — shown here, nothing saved
> - **Markdown file (.md)** — clean formatted table, downloadable
> - **Text file (.txt)** — plain text table, universal compatibility
> - **PDF (.pdf)** — formatted document, ready to print or share

Wait for their answer before producing the final output. If the user already indicated a preference earlier in the conversation, skip asking and use that.

### Table design principles

All tables must be:
- **Professional and scannable** — aligned columns, clear headers
- **Sorted by price ascending** by default
- **Highlighting the lowest price** — mark it clearly (e.g., ✓ or bold or a note)
- **Including units** where relevant (€/kg, €/L)
- **Compact** — no redundant columns, no filler text

#### Price comparison table (single product across merchants)

| Προϊόν | Κατάστημα | Τιμή | Τιμή/μονάδα |
|--------|-----------|------|-------------|
| Δέλτα Φρες γάλα πλήρες 1L | masoutis | €1.67 ✓ | €1.67/L |
| Δέλτα Φρες γάλα πλήρες 1L | ab | €1.68 | €1.68/L |

#### Basket summary table (multiple products, cheapest per item)

| Προϊόν | Φθηνότερο κατάστημα | Τιμή | 2ο φθηνότερο | Τιμή |
|--------|---------------------|------|--------------|------|
| Γάλα πλήρες 1L | masoutis | €1.67 ✓ | ab | €1.68 |
| Dettol spray 400ml | ab | €2.38 ✓ | masoutis | €3.70 |

**Winner row** (append below basket table):
> 🏆 masoutis wins on 1/2 items. Estimated total if buying all there: €X.XX

### File output rules

When producing a file, save it to the current working directory (or to the environment's outputs folder if one is provided) and tell the user where it is.

**Markdown (.md)**
- Use `##` for section headers
- Use standard markdown tables
- Include date at top: `_Σύγκριση τιμών: [date]_`
- No decorative elements — clean and functional

**Text (.txt)**
- Use ASCII table borders (e.g., `+--------+--------+`)
- Pad columns for alignment
- Include a header block with date and query summary

**PDF (.pdf)**
- Use the PDF skill if one is available; otherwise generate it with a script
- Use a clean single-column layout
- Table with alternating row shading if possible
- Footer with date and source note

---

## Step 4 — Error Handling

| Situation | Action |
|-----------|--------|
| No results | Try the Greek name, a shorter or stem word, or a brand name |
| Product not found after 2 tries | Tell the user clearly: product may not be in the database |
| Unknown merchant or category | The script prints suggestions; otherwise run `merchants` / `categories` and match |
| `Could not fetch price data` | The price source is unreachable. Tell the user, and retry once with `--refresh` |
| `uv: command not found` | Tell the user uv is required (https://docs.astral.sh/uv/) |
| Too many results | Narrow the query — never dump the full list to the user |
| Ambiguous product | Clarify before searching — do not guess |
| User asks for something unavailable (e.g., creating a basket or ordering) | Explain it's not available; offer the manual comparison approach instead |

---

## Principles

- **Less is more.** Don't narrate what you're doing. Just do it, then show the result.
- **One clarification max.** Don't ask multiple rounds of questions. Batch them into one ask if needed.
- **Never show raw script output.** Always filter and format before presenting anything to the user.
- **Don't explain the internals** (commands, categories, caching) to the user unless they specifically ask. They want prices.
