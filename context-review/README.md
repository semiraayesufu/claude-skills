# context-review

Render any folder of docs (a context kit, a knowledge base, a project wiki) as one self-contained HTML page for review: a sidebar table of contents and one collapsible card per file.

## Run it

```bash
python3 generate_review.py /path/to/your/docs ~/Desktop/REVIEW-my-docs.html
```

- No root folder? It uses the current directory.
- No output path? It writes `./REVIEW-context-layer.html`.
- No dependencies. Python 3 standard library only.

From Claude: "render this folder for review" or `/context-review`.

## What it does

1. Files at the root become a "Root" section.
2. Each top-level folder becomes a section, walked recursively.
3. Markdown is converted to HTML; other files show as escaped code blocks.
4. YAML frontmatter is stripped and its `description` shown as a subtitle.
5. Cards start collapsed; sidebar links jump to and open the exact file.
6. Empty folders are shown, not skipped.

## Make it yours

Change the font link and the CSS color variables near the top of `generate_review.py` to match your brand.

## Why local only

It's a snapshot for a specific review moment, not a living doc. Regenerate it when the folder changes, and keep it out of your repo.
