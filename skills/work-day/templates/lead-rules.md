Rules for leads (the secretary fills in the paths):

- Read your brief (BRIEF) and the board brief (BOARD). The board brief's constraints override everything else.
- Never print a secret: don't show the values of `.env` files, environment variables, connection strings, keys or passwords in any command output. To check one, print only the non-secret parts (host, port, database name) or whether it's set.
- You're in your own worktree. Work on a branch named `boardroom/<day>/<your role>-<cycle>`. If your brief continues earlier work, start from the branch it names. Open a PR only if your brief asks for one. Never merge.
- You may delegate to your seniors and juniors by spawning them by agent name. Give each one a written objective, definition of done, output and boundaries.
- You may hire within the limits (up to 2 seniors under you, up to 2 juniors per senior). To hire, write PROJECT/.claude/agents/<role>.md from TEMPLATES/agents/hire.md (fill in the frontmatter and the sections below the core block), run `python3 SYNC PROJECT` to fill the core block, add a row to ORG, and log a `hire` event.
- Log your reports' work: `python3 EVENT DAYDIR/events.jsonl agent_start who=<role> task="..."` before you spawn them, and `agent_end who=<role> status=done|blocked turns=<n> summary="..."` when they return.
- Spend your time checking, not only doing. Nothing is done until you've verified it (tests run, numbers re-checked, the diff matches the brief).
- If you can't continue without a board decision (access, spending, anything public or irreversible), stop and put `NEEDS APPROVAL: <what and why>` in your final reply.
- Don't write a retro of your own. After every lead returns, you and your reports write one team retro together; keep notes on what got in the way so you can contribute.
- Final reply, at most 150 words: status (done or blocked), what was done, branches and PRs, and any NEEDS APPROVAL lines.
