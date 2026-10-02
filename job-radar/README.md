# job-radar

Set up a scheduled job search that emails you a short, ranked list of fresh roles that fit your background. You set it up once in a conversation; after that it runs on its own.

## Use it

Ask Claude: "set up my job radar" or `/job-radar`.

Claude asks only for what it can't already find in your resume or files:

- Who you are: experience, past roles, key skills (a resume is the best source)
- Target roles, seniority and earliest start date
- Locations, preferred sectors and priority companies
- How often to run, at what times, and how many roles per email
- The email address to send to

## What it does

1. Builds a standalone search prompt from your profile.
2. Creates a scheduled task that runs at the times you chose.
3. Each run searches job boards and company career sites for roles posted in the last 7 days.
4. Skips anything already sent in the last 14 days.
5. Emails the roles, freshest and strongest first, each with a one-line reason it fits and a link.
6. Offers a test run so you can check the first email before the schedule starts.

## Requirements

- A Gmail connection in Claude, for sending the email.
- Access to scheduled tasks.

## Make it yours

There is nothing to edit in the files. Everything is set in the setup conversation, and you can change it later by asking Claude to update your job radar.

## Limits

- Boards that need a login (LinkedIn, school job portals) may return few results. Public boards and career sites make up the rest.
- Posting dates on aggregators can be wrong, so the task leaves out any role whose date it can't confirm.
