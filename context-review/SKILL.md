---
name: context-review
description: "Render any context kit or docs folder as one self-contained HTML page for stakeholder review: a sidebar table of contents plus one collapsible card per file, grouped by the folders that actually exist. Use when someone wants to share, review, or get feedback on a folder of Markdown docs, a context kit, or a knowledge base without giving reviewers repo access. Local output only, never committed."
---

# Context Review

Turn a folder of docs into one HTML page anyone can open in a browser. Reviewers see every
file, grouped by folder, without needing repo access or Claude.

## Make it yours

- **Branding:** edit the font link and the color variables (`--accent`, `--accent-soft`, `--ink`)
  near the `CSS` block in `generate_review.py`.
- **Default output name:** change `REVIEW-context-layer.html` in the same file.
- No other setup. It works with Python 3's standard library only.

## Workflow

1. Ask which folder is the root of the kit if it isn't obvious.
2. Ask where to save the output if unstated (Desktop or Downloads is a good default).
3. Run:
   ```bash
   python3 generate_review.py <root_folder> <output_path>
   ```
4. Confirm it printed the output path, then tell the user and offer to open it.
5. **Don't commit the output to a repo.** It's a snapshot for one review moment. If the user asks
   to commit it, point that out and confirm before doing it.

## What it handles

- Files at the root become a "Root" section; each top-level folder becomes its own section.
- Markdown renders as formatted HTML (headings, lists, tables, code, links, quotes).
- Other files (JSON, YAML, scripts) show as plain code blocks.
- YAML frontmatter is hidden; a `description` field shows as a subtitle.
- Cards start collapsed; clicking a sidebar link jumps to and opens that file.
- Empty folders show an honest "empty folder" note.

## Done looks like

One local HTML file a reviewer can open and read end to end. If the docs change, regenerate it.
