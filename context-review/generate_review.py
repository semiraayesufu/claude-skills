#!/usr/bin/env python3
"""
generate_review.py: render any context kit folder as a single, self
contained, browsable HTML page for stakeholder review.

Zero third party dependencies (stdlib only), so this runs anywhere Python 3
does. No pip install step needed.

Works for any team's context kit or docs folder. Point it at a root
folder and it walks that folder's actual structure directly, no manifest
schema required.
Top level files become a "Root" section; each top level subfolder becomes
its own section, recursively rendering every file inside it. This means it
adapts automatically to however a team's kit happens to be organized.

Usage:
    python3 generate_review.py [root_folder] [output_path]

If root_folder is omitted, the current directory is used. If output_path
is omitted, it defaults to ./REVIEW-context-layer.html in the current
directory.

The output file is a local review artifact. It is not meant to be
committed to a repo.
"""

import html
import os
import re
import subprocess
import sys
from datetime import datetime, timezone

SKIP_DIR_NAMES = {".git", "__pycache__", "node_modules", ".venv", "venv"}


def git_info(repo_root):
    def run(args):
        try:
            return subprocess.check_output(
                ["git"] + args, cwd=repo_root, stderr=subprocess.DEVNULL
            ).decode().strip()
        except Exception:
            return None

    branch = run(["rev-parse", "--abbrev-ref", "HEAD"]) or "unknown"
    sha = run(["rev-parse", "--short", "HEAD"]) or "unknown"
    return branch, sha


# ---------------------------------------------------------------------------
# Minimal self contained Markdown to HTML: headers, bold/italic, inline
# code, fenced code, links, lists, pipe tables, blockquotes, horizontal
# rules. Not a general purpose CommonMark renderer, just enough for typical
# context kit docs.
# ---------------------------------------------------------------------------

def esc(s):
    return html.escape(s, quote=False)


def inline_md(s):
    s = esc(s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<em>\1</em>", s)
    return s


def strip_frontmatter(text):
    """Strip a leading --- ... --- YAML frontmatter block, if present.
    Returns (description_or_None, remaining_text)."""
    if not text.startswith("---"):
        return None, text
    lines = text.split("\n")
    if lines[0].strip() != "---":
        return None, text
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            fm = "\n".join(lines[1:i])
            rest = "\n".join(lines[i + 1:])
            m = re.search(r'^description:\s*"?(.*?)"?\s*$', fm, re.MULTILINE)
            desc = m.group(1) if m else None
            return desc, rest
    return None, text


def md_to_html(text):
    lines = text.split("\n")
    out = []
    para = []
    i, n = 0, len(lines)

    def flush_para():
        if para:
            out.append("<p>" + inline_md(" ".join(para).strip()) + "</p>")
            para.clear()

    while i < n:
        raw_line = lines[i]
        line = raw_line.strip()

        if line.startswith("```"):
            flush_para()
            lang = line[3:].strip()
            i += 1
            code_lines = []
            while i < n and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            i += 1
            cls = f' class="language-{esc(lang)}"' if lang else ""
            out.append(f"<pre><code{cls}>{esc(chr(10).join(code_lines))}</code></pre>")
            continue

        if re.match(r"^(-{3,}|\*{3,})$", line):
            flush_para()
            out.append("<hr>")
            i += 1
            continue

        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            flush_para()
            level = len(m.group(1))
            out.append(f"<h{level}>{inline_md(m.group(2))}</h{level}>")
            i += 1
            continue

        if line.startswith(">"):
            flush_para()
            quote_lines = []
            while i < n and lines[i].strip().startswith(">"):
                quote_lines.append(re.sub(r"^\s*>\s?", "", lines[i]))
                i += 1
            out.append("<blockquote>" + md_to_html("\n".join(quote_lines)) + "</blockquote>")
            continue

        if "|" in line and i + 1 < n and re.match(
            r"^\s*\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)+\|?\s*$", lines[i + 1]
        ):
            flush_para()
            header_cells = [c.strip() for c in line.strip("|").split("|")]
            i += 2
            rows = []
            while i < n and "|" in lines[i] and lines[i].strip():
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            thead = "<tr>" + "".join(f"<th>{inline_md(c)}</th>" for c in header_cells) + "</tr>"
            tbody = "".join(
                "<tr>" + "".join(f"<td>{inline_md(c)}</td>" for c in row) + "</tr>"
                for row in rows
            )
            out.append(f"<table><thead>{thead}</thead><tbody>{tbody}</tbody></table>")
            continue

        if re.match(r"^[-*]\s+", line):
            flush_para()
            items = []
            while i < n and re.match(r"^[-*]\s+", lines[i].strip()):
                items.append(inline_md(re.sub(r"^[-*]\s+", "", lines[i].strip())))
                i += 1
            out.append("<ul>" + "".join(f"<li>{it}</li>" for it in items) + "</ul>")
            continue

        if re.match(r"^\d+\.\s+", line):
            flush_para()
            items = []
            while i < n and re.match(r"^\d+\.\s+", lines[i].strip()):
                items.append(inline_md(re.sub(r"^\d+\.\s+", "", lines[i].strip())))
                i += 1
            out.append("<ol>" + "".join(f"<li>{it}</li>" for it in items) + "</ol>")
            continue

        if line == "":
            flush_para()
            i += 1
            continue

        para.append(line)
        i += 1

    flush_para()
    return "\n".join(out)


# ---------------------------------------------------------------------------
# Page assembly
# ---------------------------------------------------------------------------

FONT_IMPORT = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
    '<link href="https://fonts.googleapis.com/css2?family=Libre+Franklin:ital,wght@0,400;0,500;0,600;0,700;1,400&display=swap" rel="stylesheet">'
)
# MAKE IT YOURS: change the font link above and the color variables below
# to match your team's brand. Default font is Libre Franklin, loaded from
# Google Fonts, so
# this page needs a live connection the first time a browser renders it
# with the real font. It falls back to the system sans serif stack
# gracefully if offline.
#
# Default palette: neutral black, white and grey. --accent and
# --accent-soft are the easiest places to add a brand color.
CSS = """
:root {
  --bg:#ffffff; --card:#ffffff; --ink:#121212; --body:#1a1a1a; --muted:#666666;
  --line:#e2e2e2; --line2:#d0d0d0; --accent:#121212; --accent-soft:#f2f2f2;
}
* { box-sizing:border-box; }
body { margin:0; background:var(--bg); color:var(--body);
  font-family:"Libre Franklin",-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
  line-height:1.62; font-size:16px; }
.layout { display:flex; max-width:1200px; margin:0 auto; }
nav.toc { width:220px; flex:0 0 220px; padding:40px 16px; position:sticky; top:0; height:100vh;
  overflow-y:auto; border-right:1px solid var(--line); font-size:0.86rem; }
nav.toc a { display:block; color:var(--muted); text-decoration:none; padding:4px 8px; border-radius:6px; }
nav.toc a:hover { background:var(--accent-soft); color:var(--accent); text-decoration:underline; }
nav.toc .sec-link { font-weight:700; color:var(--ink); margin-top:14px; }
.page { flex:1; max-width:860px; padding:40px 32px 140px; }
h1,h2,h3 { font-family:"Libre Franklin",-apple-system,sans-serif; color:var(--ink); font-weight:700; letter-spacing:-0.01em; }
.masthead { border-bottom:2px solid var(--ink); padding-bottom:20px; margin-bottom:36px; }
.eyebrow { text-transform:uppercase; letter-spacing:0.14em; font-size:0.7rem; font-weight:700; color:var(--muted); }
.masthead h1 { font-size:2.1rem; margin:10px 0 10px; }
.masthead p { color:var(--muted); margin:0; font-size:0.95rem; }
section.folder { margin:0 0 48px; padding-top:8px; border-top:1px solid var(--line); }
section.folder:first-of-type { border-top:none; }
section.folder > h2 { font-size:1.5rem; margin:20px 0 18px; color:var(--accent); }
.filecard { background:var(--card); border:1px solid var(--line2); border-radius:10px;
  padding:20px 24px; margin:0 0 20px; }
.filecard .path { font-family:"SF Mono",Menlo,Consolas,monospace; font-size:0.76rem;
  color:var(--muted); text-transform:none; letter-spacing:0; margin-bottom:12px;
  display:inline-block; background:var(--accent-soft); padding:3px 9px; border-radius:5px; }
.filecard h1 { font-size:1.25rem; margin:0 0 10px; }
.filecard h2 { font-size:1.08rem; margin:20px 0 8px; }
.filecard h3 { font-size:0.98rem; margin:16px 0 6px; }
.filecard p { margin:0 0 12px; font-size:0.94rem; }
.filecard ul, .filecard ol { margin:0 0 12px; padding-left:22px; font-size:0.94rem; }
.filecard li { margin:4px 0; }
.filecard code { background:#f0f0f0; padding:1px 5px; border-radius:4px; font-size:0.85em; }
.filecard pre { background:#f0f0f0; padding:14px 16px; border-radius:8px; overflow-x:auto; font-size:0.78rem; }
.filecard pre code { background:none; padding:0; }
.filecard blockquote { border-left:3px solid var(--line2); margin:0 0 12px; padding:2px 0 2px 16px;
  color:var(--muted); font-size:0.92rem; }
.filecard table { width:100%; border-collapse:collapse; font-size:0.82rem; margin:0 0 14px; }
.filecard th, .filecard td { text-align:left; padding:8px 10px; border-bottom:1px solid var(--line); vertical-align:top; }
.filecard th { background:#f5f5f5; font-weight:600; color:var(--muted);
  font-size:0.68rem; text-transform:uppercase; letter-spacing:0.05em; }
.filecard strong { color:var(--ink); }
.empty-note { color:var(--muted); font-style:italic; font-size:0.88rem; }
.skill-desc { color:var(--muted); font-style:italic; font-size:0.88rem; margin:-6px 0 12px; }
details.raw { background:var(--card); border:1px solid var(--line2); border-radius:10px; padding:14px 20px; margin:0 0 16px; scroll-margin-top:20px; }
details.raw summary { cursor:pointer; font-weight:600; color:var(--accent); font-size:0.92rem; font-family:"SF Mono",Menlo,Consolas,monospace; }
details.raw .filecard { border:none; padding:16px 0 0; margin:0; }
details.raw:target, details.raw.js-highlight { outline:2px solid var(--ink); outline-offset:2px; }
@media (max-width:900px) { nav.toc { display:none; } .layout { display:block; } .page { max-width:none; } }
"""

JUMP_TO_FILE_JS = """
function openTargetFile() {
  var hash = decodeURIComponent(location.hash.slice(1));
  if (!hash) return;
  var el = document.getElementById(hash);
  if (!el) return;
  var details = el.tagName === 'DETAILS' ? el : el.closest('details');
  if (details) { details.open = true; details.classList.add('js-highlight'); }
  el.scrollIntoView({block: 'start'});
}
window.addEventListener('hashchange', openTargetFile);
window.addEventListener('DOMContentLoaded', openTargetFile);
"""


def slugify(rel_path):
    """A stable, unique anchor id for a given file path. The 'file-' prefix
    keeps it from ever colliding with a section id."""
    return "file-" + re.sub(r"[^a-z0-9]+", "-", rel_path.lower()).strip("-")


def render_file_card(rel_path, source_text, as_raw=False, extra_desc=None):
    """Every real file card renders collapsed by default: click to read, or
    follow a sidebar link straight to it. Keeps a folder with many docs
    scannable instead of one long scroll. Returns (html, slug) so the
    caller can point a precise sidebar link at this exact file."""
    body = ""
    if extra_desc:
        body += f'<p class="skill-desc">{inline_md(extra_desc)}</p>'
    if as_raw:
        body += f"<pre><code>{esc(source_text)}</code></pre>"
    else:
        desc, rest = strip_frontmatter(source_text)
        if desc and not extra_desc:
            body += f'<p class="skill-desc">{inline_md(desc)}</p>'
        body += md_to_html(rest)
    card = f'<div class="filecard"><div class="path">{esc(rel_path)}</div>{body}</div>'
    slug = slugify(rel_path)
    return f'<details class="raw" id="{slug}"><summary>{esc(rel_path)}</summary>{card}</details>', slug


def render_placeholder(rel_path, message):
    """An empty folder note. Gets its own anchor so a sidebar link to it
    still works, but is not collapsible since there is nothing to expand."""
    slug = slugify(rel_path)
    card = (
        f'<div class="filecard" id="{slug}"><div class="path">{esc(rel_path)}</div>'
        f'<p class="empty-note">{esc(message)}</p></div>'
    )
    return card, slug


def read(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def build_toc(sections):
    """Each entry in files is (display_name, slug): a precise per file
    anchor, not just the shared section anchor, so clicking a sidebar link
    jumps straight to (and expands) that exact file."""
    parts = []
    for sec_id, sec_title, files in sections:
        parts.append(f'<a class="sec-link" href="#{sec_id}">{esc(sec_title)}</a>')
        for display_name, slug in files:
            parts.append(f'<a href="#{slug}">{esc(display_name)}</a>')
    return "".join(parts)


def render_file_body(rel_path, source_text, as_raw):
    """Render a single file's body (no outer collapsible wrapper, no
    top-level anchor) -- used inside a grouped block where the group as a
    whole is already collapsible, so wrapping every file inside it in its
    own <details> too would just be a second click for no reason."""
    body = ""
    if as_raw:
        body += f"<pre><code>{esc(source_text)}</code></pre>"
    else:
        desc, rest = strip_frontmatter(source_text)
        if desc:
            body += f'<p class="skill-desc">{inline_md(desc)}</p>'
        body += md_to_html(rest)
    return f'<div class="filecard"><div class="path">{esc(rel_path)}</div>{body}</div>'


def render_group(dir_path, rel_root, skip=None):
    """Render every file under dir_path, recursively, as plain (uncollapsed)
    file cards -- the caller wraps the whole thing in one <details>. `skip`
    is an absolute path to leave out (used when its README.md was already
    broken out and rendered separately). Returns (html, file_count)."""
    parts = []
    count = 0
    for cur_root, dirs, filenames in os.walk(dir_path):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIR_NAMES and not d.startswith("."))
        for fname in sorted(filenames):
            if fname.startswith("."):
                continue
            full = os.path.join(cur_root, fname)
            if skip and os.path.abspath(full) == skip:
                continue
            rel = os.path.relpath(full, rel_root)
            try:
                source = read(full)
            except (UnicodeDecodeError, OSError):
                continue
            is_md = fname.lower().endswith(".md")
            parts.append(render_file_body(rel, source, as_raw=not is_md))
            count += 1
    return "".join(parts), count


def render_dir(dir_path, rel_root):
    """Render one folder's contents for a section (or a group inside one):
    a file directly inside becomes its own file card and its own sidebar
    entry, same as before. A *subfolder* becomes one grouped, collapsible
    block containing everything inside it (recursively), with a single
    sidebar entry for the whole group -- so a skill with a dozen small
    files (README, SKILL.md, scripts/, templates/, ...) shows up as one
    named, collapsible item in the sidebar instead of flooding it with
    every file inside. Returns (toc_entries, html_body)."""
    toc_entries, body_parts = [], []

    entries = sorted(os.listdir(dir_path))
    direct_files = [
        e for e in entries
        if os.path.isfile(os.path.join(dir_path, e)) and not e.startswith(".")
    ]
    subdirs = [
        e for e in entries
        if os.path.isdir(os.path.join(dir_path, e)) and e not in SKIP_DIR_NAMES and not e.startswith(".")
    ]

    for fname in direct_files:
        full = os.path.join(dir_path, fname)
        rel = os.path.relpath(full, rel_root)
        try:
            source = read(full)
        except (UnicodeDecodeError, OSError):
            continue
        is_md = fname.lower().endswith(".md")
        card, slug = render_file_card(rel, source, as_raw=not is_md)
        toc_entries.append((fname, slug))
        body_parts.append(card)

    for sub in subdirs:
        sub_path = os.path.join(dir_path, sub)
        rel_dir = os.path.relpath(sub_path, rel_root)

        # Break the README out of the group: it's the "what is this" file,
        # so it gets its own visible sidebar entry instead of being buried
        # one click deep inside the rest of the folder's implementation
        # detail (SKILL.md, config.json, scripts/, ...).
        readme_full = None
        for cand in sorted(os.listdir(sub_path)):
            if cand.lower() == "readme.md" and os.path.isfile(os.path.join(sub_path, cand)):
                readme_full = os.path.abspath(os.path.join(sub_path, cand))
                break
        if readme_full:
            rel = os.path.relpath(readme_full, rel_root)
            try:
                source = read(readme_full)
                card, slug = render_file_card(rel, source, as_raw=False)
                toc_entries.append((f"{sub}/README.md", slug))
                body_parts.append(card)
            except (UnicodeDecodeError, OSError):
                readme_full = None

        group_html, file_count = render_group(sub_path, rel_root, skip=readme_full)
        if file_count:
            slug = slugify(rel_dir + "/")
            body_parts.append(f'<details class="raw" id="{slug}"><summary>{esc(sub)}/</summary>{group_html}</details>')
            toc_entries.append((f"{sub}/", slug))
        elif not readme_full:
            slug = slugify(rel_dir + "/")
            body_parts.append(f'<details class="raw" id="{slug}"><summary>{esc(sub)}/ (empty)</summary></details>')
            toc_entries.append((f"{sub}/", slug))

    if not toc_entries:
        rel_dir = os.path.relpath(dir_path, rel_root) + "/"
        card, slug = render_placeholder(rel_dir, "Empty folder.")
        toc_entries.append(("(empty)", slug))
        body_parts.append(card)

    return toc_entries, "".join(body_parts)


def main():
    args = [a for a in sys.argv[1:]]
    root_folder = os.path.abspath(args[0]) if args else os.getcwd()
    out_path = args[1] if len(args) > 1 else "./REVIEW-context-layer.html"

    if not os.path.isdir(root_folder):
        raise SystemExit(f"Not a directory: {root_folder}")

    branch, sha = git_info(root_folder)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    sections = []  # (id, title, [(display_name, slug) for TOC], html_body)

    # --- Root: files directly inside root_folder, no subfolders ---
    root_files, root_body = [], []
    for fname in sorted(os.listdir(root_folder)):
        full = os.path.join(root_folder, fname)
        if not os.path.isfile(full) or fname.startswith("."):
            continue
        try:
            source = read(full)
        except (UnicodeDecodeError, OSError):
            continue
        is_md = fname.lower().endswith(".md")
        card, slug = render_file_card(fname, source, as_raw=not is_md)
        root_files.append((fname, slug))
        root_body.append(card)
    if root_files:
        sections.append(("root", "Root", root_files, "".join(root_body)))

    # --- One section per top level subfolder, walked recursively ---
    for entry in sorted(os.listdir(root_folder)):
        full = os.path.join(root_folder, entry)
        if not os.path.isdir(full) or entry in SKIP_DIR_NAMES or entry.startswith("."):
            continue
        files, body = render_dir(full, root_folder)
        sec_id = re.sub(r"[^a-z0-9]+", "-", entry.lower()).strip("-") or "section"
        sections.append((sec_id, f"{entry}/", files, body))

    toc_html = build_toc([(s[0], s[1], s[2]) for s in sections])
    sections_html = "".join(
        f'<section class="folder" id="{sec_id}"><h2>{esc(title)}</h2>{body}</section>'
        for sec_id, title, _files, body in sections
    )

    kit_name = os.path.basename(root_folder.rstrip("/")) or root_folder
    parent_name = os.path.basename(os.path.dirname(root_folder.rstrip("/")))
    eyebrow = parent_name if parent_name else "Context Kit"

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(kit_name)} context kit review</title>
{FONT_IMPORT}
<style>{CSS}</style>
</head>
<body>
<div class="layout">
<nav class="toc">{toc_html}</nav>
<div class="page">
  <div class="masthead">
    <div class="eyebrow">{esc(eyebrow)}</div>
    <h1>{esc(kit_name)} · Full Tree</h1>
    <p>Rendered from <code>{esc(kit_name)}/</code> for review. This is a local snapshot,
    not a file in the repo, and it does not update itself; re-run this script to refresh
    it after the kit changes.
    Branch <code>{esc(branch)}</code>, commit <code>{esc(sha)}</code>. Regenerated {now}.</p>
  </div>
  {sections_html}
</div>
</div>
<script>{JUMP_TO_FILE_JS}</script>
</body>
</html>
"""

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(page)

    print(f"Wrote {os.path.abspath(out_path)}")


if __name__ == "__main__":
    main()
