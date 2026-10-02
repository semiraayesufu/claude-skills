# Claude Skills

Skills I've built for Claude that turn repeat work into one-line requests. Each one is generic: add it to Claude, fill in the "Make it yours" settings, and it adapts to you.

| Skill | What it does | You give it | You get |
|---|---|---|---|
| [job-radar](job-radar/SKILL.md) | Sets up a scheduled job search that emails you fresh roles that fit your background | Your resume, target roles, cities, schedule | A short, ranked email of roles posted in the last 7 days, on your schedule |
| [category-summary](category-summary/SKILL.md) | Turns rough weekly notes into a one-page leadership report | A few bullet points on what you saw this week | A formatted `.docx` with a health snapshot, takeaways, cited market signals and recommendations |
| [context-review](context-review/SKILL.md) | Renders a folder of docs as one shareable HTML page | A folder path | A single HTML file reviewers can open in any browser |

## How to use a skill

1. Download the skill's folder.
2. Add it to Claude: upload the folder (or a zip of it) in Claude's skills settings, or place it in `~/.claude/skills/` for Claude Code.
3. Open the skill's `SKILL.md` and fill in its **Make it yours** section.
4. Ask Claude in plain language, e.g. "set up my job radar," "help me with my weekly report," or "render this folder for review."

## Requirements

- **job-radar:** a Gmail connection for delivery and access to scheduled tasks.
- **category-summary:** Node.js and the `docx` package (`npm install -g docx`).
- **context-review:** Python 3. No extra packages.

## About

Built by [Semira Yesufu](https://semiraworks.framer.website): strategist, designer, builder.
