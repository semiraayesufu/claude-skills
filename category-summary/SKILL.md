---
name: category-summary
description: >
  Turns a category or market specialist's rough weekly notes into a polished one-page
  leadership report (.docx). Use whenever someone mentions a weekly report, category summary,
  category performance update, market update for leadership, or says "help me with my weekly
  report" or "write up this week's category summary."
---

# Category Summary

Turn a specialist's raw weekly observations into a leadership-ready one-page `.docx` report.
The specialist shares notes. You produce the structure, the insights and the formatting.

**The specialist should never have to think about** report structure, what the trend is,
what the risks or opportunities are, or how to phrase recommendations. Their only job is to
share what they saw this week.

## Make it yours (one-time setup)

Edit the `BRAND` block at the top of `scripts/generate-report.js`:

| Setting | What it controls | Example |
|---|---|---|
| `company` | Name shown top left of every page | `"Acme Marketplace"` |
| `reportTitle` | Text shown top right | `"Weekly Category Summary"` |
| `accent` | Hex color for rules, citations, Field Insight bar | `"2563eb"` |
| `accentWash` | Light tint of the accent for the Field Insight box | `"eef4ff"` |
| `footer` | Footer text | `"Confidential · Internal Use Only"` |

Optional: rename the snapshot labels (Demand Trend, Competitive Pressure) and section names
in the script to match the words your team uses.

---

## Conversation flow

### Step 1: Category and period
Ask exactly:
> Let's get started. What category are you reporting on, and what period does this summary cover?

Accept any format. Move on.

### Step 2: Weekly observations
Ask exactly:
> What stood out this week? Share a few notes or bullet points. I'll organize them into the report.

Accept anything: demand shifts, customer complaints, supply or partner changes, competitor
activity, regional patterns, or "nothing major this week." Don't ask follow-ups about format.

### Step 3: Optional context
Ask exactly:
> Anything else you'd like included before I generate the report?

If they say no or skip, go straight to Step 4. Never ask them for risks, opportunities or
recommendations; those are outputs.

### Step 4: External research
Research only topics that appear in the specialist's notes (competitor pricing or promotions,
market shifts, industry news). Use web search or any research tool available.
- Every external claim gets a source name and date.
- If a claim can't be verified, leave it out entirely.

### Step 5: Analysis (internal, not shown)
Derive these yourself from the notes and research:
- **Demand Trend:** Increasing / Stable / Decreasing
- **Competitive Pressure:** Low / Moderate / High
- **Key Risk:** one sentence
- **Key Opportunity:** one sentence
- **Key Takeaways:** max 3 bullets
- **Recommendations:** max 2 bullets, each traceable to a specific observation

### Step 6: Generate the report
If a docx skill is available, read it first.

```bash
npm install -g docx
```

Fill the `data` object in `scripts/generate-report.js` with the analysis and observations, then:

```bash
node scripts/generate-report.js "[category]-weekly-[period].docx"
```

Validate the file if a docx validator is available, then share it with the user.

---

## Report layout

```
[Company name]                              [Report title]
──────────────────────── accent rule ────────────────────────
[Category name]                              23pt
[Period] · Prepared by: [Name]               8.5pt, muted

CATEGORY HEALTH SNAPSHOT
  Demand Trend        | Competitive Pressure   (color-coded)
  Key Risk            | Key Opportunity

KEY TAKEAWAYS                        max 3 bullets
DEMAND & PERFORMANCE SIGNALS         max 4 bullets (specialist notes only)
COMPETITIVE PRICING & MARKET SIGNALS max 2 bullets, cited
FIELD INSIGHT                        optional callout
RECOMMENDATIONS                      max 2 bullets

External [1] Source (Date) · Internal: Specialist observations
[Footer text]                                         Page N
```

## Writing rules

- No em dashes.
- No invented percentages or metrics unless the specialist provided them or a source is cited.
- Don't turn qualitative notes into numbers.
- Bullets are short and declarative, two lines max.
- Demand & Performance Signals come only from the specialist's notes, not research.
- Every recommendation traces back to something in the report.

## Principle

The specialist should feel like they're handing notes to a colleague, not filling out a form.
The fewer questions you ask, the more they'll use it.
