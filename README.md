# Claude Skills

Skills I've built for Claude that turn repeat work into one-line requests. Each one is generic: add it to Claude, fill in the "Make it yours" settings, and it adapts to you.

| Skill | What it does | You give it | You get |
|---|---|---|---|
| [job-radar](job-radar/README.md) | Sets up a scheduled job search that emails you fresh roles that fit your background | Your resume, target roles, cities, schedule | A short, ranked email of roles posted in the last 7 days, on your schedule |
| [category-summary](category-summary/README.md) | Turns rough weekly notes into a one-page leadership report | A few bullet points on what you saw this week | A formatted `.docx` with a health snapshot, takeaways, cited market signals and recommendations |

## How to use a skill

1. Download the skill's folder.
2. Add it to Claude: upload the folder (or a zip of it) in Claude's skills settings, or place it in `~/.claude/skills/` for Claude Code.
3. Read the skill's `README.md` for setup, including any **Make it yours** settings.
4. Ask Claude in plain language, e.g. "set up my job radar" or "help me with my weekly report."

## Requirements

- **job-radar:** a Gmail connection for delivery and access to scheduled tasks.
- **category-summary:** Node.js and the `docx` package (`npm install -g docx`).

## About

Built by [Semira Yesufu](https://semiraworks.framer.website): strategist, designer, builder.
