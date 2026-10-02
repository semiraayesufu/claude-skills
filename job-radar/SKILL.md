---
name: "job-radar"
description: "Set up a recurring scheduled task that emails someone fresh, targeted job roles (posted within 7 days) on their chosen schedule, tailored to their background and targets."
---

# Job Radar

Build a personal job-alert that runs on a schedule, searches the web for fresh roles that fit the person, and emails a short, ranked list. You set it up once; it runs in fresh sessions after that.

## Step 1: Gather the profile

Check memory, project files, and any attached resume first. Only ask (with AskUserQuestion, batched into one call where possible) for what's missing:

1. **Who they are:** degree and grad date, years of experience, key past roles, signature skills. A resume is the best source.
2. **Target roles:** titles and tracks (e.g. PM, strategy, data, design). Note if they keep separate resume versions per track.
3. **Seniority / timing:** new grad, MBA full-time, experienced, intern; earliest start date.
4. **Locations:** country, priority cities, remote OK, any bonus international cities.
5. **Sectors:** preferred industries (preference, not a hard filter, unless they say so).
6. **Priority companies:** warm or cold leads whose career sites get checked every run.
7. **Sources:** default set below, plus any boards they name (e.g. Jobright.ai, school job boards).
8. **Cadence and volume:** times of day, timezone, roles per run.
9. **Freshness window:** default 7 days, newest first.
10. **Delivery:** email address (Gmail connector required) and whether they also want push notifications.

If Gmail isn't connected, say so and suggest connecting it, or fall back to push notifications only.

## Step 2: Write the scheduled-task prompt

Every run starts with no memory, so the prompt must be fully standalone. Use this template and fill every bracket:

```
You are running a recurring job search for [Name]. Find the [N] BEST fresh roles that fit them, then email them via the Gmail connector (send_message to [email]). This runs [cadence] ([times + timezone]). Quality over quantity.

## Who they are
[Grad date / experience, past roles, skills, positioning in 3-5 bullets]

## Roles to search
[Titles by track. Exclusions, e.g. internships, part-time, wrong seniority.]

## Location
[Country. Priority cities. Remote rules. Optional bonus international section.]

## Sectors (preferred, not required)
[List]

## FRESHNESS (strict)
Only include roles posted within the last [7] days. Prioritize the last 1-2 days. Every role must show a posted date or "posted X days ago". If you can't confirm the date, leave it out. Verify each link is an open posting.

## Where to search (WebSearch/WebFetch; several sources every run)
- Job boards: LinkedIn Jobs (past 24h / past week), Indeed, Glassdoor, Wellfound, Built In, Jobright.ai, [their extra boards], plus ATS pages via search (site:boards.greenhouse.io, site:jobs.lever.co, site:jobs.ashbyhq.com, myworkdayjobs.com).
- Company career sites: always check [priority companies] every run. Rotate through other strong companies in their sectors: [examples]. Vary the rotation each run.
- If a source blocks access, skip it. Never use curl/python to bypass blocked sites.

## No repeats
Before choosing, search Gmail for earlier emails with subject starting "Job Radar" from the last 14 days and exclude any role (same company + title) already sent.

## Email format
Subject: "Job Radar: [N] fresh roles ([run label], [Mon DD])"
1. One-line summary naming the top pick.
2. Priority-company line: new relevant postings, or "no new matching roles".
3. The roles, freshest and strongest first. For each: Title, Company (sector) / Location | Posted | Source / Fit: one sentence on why it fits and which resume to use / Link.
Tone: [their preferred tone]. Keep it concise.

If you can't find [N] roles meeting the freshness rule, send what you found and say why. Never pad with stale or unverified roles.
```

## Step 3: Create the scheduled task

- Use `create_trigger` (never local cron tools). Load it with ToolSearch if deferred.
- One task can cover several daily times when they share a minute: `CRON_TZ=<IANA tz> 52 11,21 * * *`.
- For times on the hour or half hour, shift a few minutes earlier to avoid congestion, and tell the user the exact times.
- Set `notifications` to match their delivery choice. Set `initiation: human_request`.
- Confirm in one or two sentences: schedule, roles per run, delivery, and the task's approval setting from the result.

## Step 4: Offer a test run

Offer to fire the task once now (`fire_trigger`) so they can check the first email before the schedule kicks in.

## Changing it later

Use `update_trigger` with the trigger ID (find it via `list_triggers`). Rewrite the whole prompt when targets change; change only `cron_expression` for timing. Don't delete and recreate.

## Honest limits to mention once

- Some boards (LinkedIn, school portals like MBA Exchange) need a login, so results from them may be thin. Public boards and career sites make up the rest.
- Posting dates on aggregators can be wrong; the task skips anything it can't confirm.
