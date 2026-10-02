# category-summary

Turn a category or market specialist's rough weekly notes into a polished one-page leadership report (`.docx`). You share what you saw this week; Claude works out the structure, the insights and the formatting.

## Use it

Ask Claude: "help me with my weekly report" or `/category-summary`.

Claude asks three short questions:

1. What category and period the report covers.
2. What stood out this week (any notes or bullet points).
3. Whether there is anything else to include.

It never asks you for risks, opportunities or recommendations. Those are what it produces.

## What you get

A one-page `.docx` with:

- **Category Health Snapshot:** demand trend and competitive pressure (color-coded), plus the key risk and key opportunity
- **Key Takeaways:** up to 3 bullets
- **Demand & Performance Signals:** up to 4 bullets, from your notes only
- **Competitive Pricing & Market Signals:** up to 2 bullets, each with a cited source
- **Field Insight:** an optional callout
- **Recommendations:** up to 2 actions, each traceable to an observation
- **Sources:** external sources with dates, and internal ones

## Requirements

- Node.js
- The `docx` package: `npm install -g docx`

## Make it yours

Edit the `BRAND` block at the top of `scripts/generate-report.js`:

| Setting | What it controls |
|---|---|
| `company` | Name shown top left of every page |
| `reportTitle` | Text shown top right |
| `accent` | Hex color for rules, citations and the Field Insight bar |
| `accentWash` | Light tint of the accent for the Field Insight box |
| `footer` | Footer text |

You can also rename the snapshot labels and section names in the script to match the words your team uses.

## Run the script directly

Fill in the `data` object in `scripts/generate-report.js`, then:

```bash
node scripts/generate-report.js "my-category-weekly.docx"
```

## Files

- `SKILL.md`: the instructions Claude follows
- `scripts/generate-report.js`: builds the `.docx`
