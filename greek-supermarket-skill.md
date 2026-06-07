---
name: greek-supermarket
description: "Use this skill for ANY query involving the greek-supermarket MCP server. Covers product search, price comparison, shopping list optimization, merchant lookup, and category browsing. Trigger on phrases like: \"find me\", \"cheapest\", \"supermarket\", \"price of\", \"compare prices\", \"shopping list\", \"καλάθι\", \"τιμή\", \"φθηνότερο\", \"σούπερ μάρκετ\", \"προϊόν\", \"κατάστημα\", or any request involving food, household, or personal care products across Greek supermarkets. Always use this skill before calling any greek-supermarket tool — it governs reasoning, clarification, tool sequencing, and output formatting."
---

# Greek Supermarket MCP Skill

## Available Tools

| Tool | Purpose |
|------|---------|
| `get_categories` | Full list of product categories (exact names required for other tools) |
| `get_products_by_category` | All products + prices across merchants for a category |
| `get_products_by_merchant` | All products sold by a specific merchant |
| `get_merchants` | Full list of merchant names |
| `get_number_of_products` | Total product count (useful for context) |

---

## Step 1 — Reasoning Before Calling Any Tool

Before calling anything, think through what the user actually needs.

### Ambiguity check

Users often ask for things that map to many products. Examples:

- "chicken" → could be whole chicken, breast fillet, thigh, frozen, fresh, by brand
- "soap" → hand soap, dish soap, laundry soap, bar soap, liquid soap
- "coffee" → instant, filter, espresso, capsules, decaf, by brand
- "milk" → full fat, semi, skimmed, plant-based, evaporated, condensed

**If the request is ambiguous**, do NOT call tools yet. Explain to the user:
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
3. Proceed category by category, not all at once.
4. After fetching each category, filter to only the relevant products, then show a comparison table.
5. At the end, produce a **basket summary table** showing: for each item, the cheapest available price and where to buy it. Include a "single best store" recommendation if one store wins on most items.

---

## Step 2 — Tool Sequencing

Always follow this order:

```
1. get_categories          ← only if you don't already know the category name
2. get_products_by_category ← fetch the relevant category
3. Filter in memory        ← find the specific product(s) the user wants
4. If not found → re-fetch or try a different category
5. Format output
```

### Category name rules
- Category names must be **exact** (as returned by `get_categories`). Never guess.
- If unsure which category a product belongs to, call `get_categories` first and reason over the list.
- Cache: if `get_categories` was already called in this conversation, reuse the result — do not call it again.

### Large response handling
Some categories return very large payloads (>1MB). When this happens:
- The result is automatically saved to `/mnt/user-data/tool_results/`
- Use `bash_tool` with `grep -i "search_term"` on the saved file path to extract matching products
- Then format only the matched products — do not attempt to load the entire file into context
- If the grep returns nothing, try alternate spellings or a broader term
- If still nothing, re-fetch with a different category and repeat

Example grep pattern:
```bash
grep -i "dettol" /mnt/user-data/tool_results/<filename>.json | head -80
```

### Merchant lookup
Use `get_products_by_merchant` when:
- The user asks "what does [store] sell?" or "what's available at [store]?"
- You need to verify if a specific merchant carries a product
- Building a single-store shopping list

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
- **Including units** where relevant (€/kg, €/500ml, etc.)
- **Compact** — no redundant columns, no filler text

#### Price comparison table (single product across merchants)

| Προϊόν | Κατάστημα | Τιμή | Τιμή/kg |
|--------|-----------|------|---------|
| Πίνδος κοτόπουλο νωπό | Sklavenitis | €2.65 ✓ | €2.65/kg |
| Πίνδος κοτόπουλο νωπό | Masoutis | €3.75 | €3.75/kg |

#### Basket summary table (multiple products, cheapest per item)

| Προϊόν | Φθηνότερο κατάστημα | Τιμή | 2ο φθηνότερο | Τιμή |
|--------|---------------------|------|--------------|------|
| Κοτόπουλο /kg | Sklavenitis | €2.65 ✓ | Masoutis | €3.75 |
| Dettol 750ml | Sklavenitis | €2.00 ✓ | Mymarket | €2.25 |
| Dimello Forza 250g | Xalkiadakis | €5.56 ✓ | Sklavenitis | €6.02 |

**Winner row** (append below basket table):
> 🏆 Sklavenitis wins on 2/3 items. Estimated total if buying all there: €X.XX

### File output rules

When producing a file:

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
- Read `/mnt/skills/public/pdf/SKILL.md` before generating
- Use a clean single-column layout
- Table with alternating row shading if the PDF skill supports it
- Footer with date and source note

Save all files to `/mnt/user-data/outputs/` and present with `present_files`.

---

## Step 4 — Error Handling

| Situation | Action |
|-----------|--------|
| Tool returns empty result | Try adjacent category or re-fetch with broader term |
| Product not found after 2 tries | Tell the user clearly: product may not be in the database |
| Merchant name unknown | Call `get_merchants` first, then match |
| Response too large (stored to disk) | Grep the saved file — never skip this step |
| Ambiguous product | Clarify before fetching — do not guess |
| User asks for unavailable feature (e.g., create_basket) | Explain it's not available; offer the manual comparison approach instead |

---

## Principles

- **Less is more.** Don't narrate what you're doing. Just do it, then show the result.
- **One clarification max.** Don't ask multiple rounds of questions. Batch them into one ask if needed.
- **Never show raw API output.** Always filter and format before presenting anything to the user.
- **Don't explain the MCP internals** to the user unless they specifically ask. They don't care about categories or tool names — they want prices.