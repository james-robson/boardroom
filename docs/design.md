# Boardroom — design

Status: **draft, first version being built**. Background is in [origin-conversation.md](origin-conversation.md) and [research.md](research.md).

Boardroom is a framework, not tied to any one project. You install it as a Claude Code plugin, run Claude Code inside a target project, and run `/work-day`. Everything specific to a project lives in that project's repo: its board brief, its staff, its memory and its history.

## The rule

Agents propose and build. The board (the human) approves anything that ships, spends money, goes public or changes the org beyond its limits.

## Where things live

**This repo (the framework)**

```
.claude-plugin/
  plugin.json             # plugin manifest
  marketplace.json        # lets this repo be added as a local marketplace
skills/work-day/
  SKILL.md                # the day's procedure
  templates/              # board brief, decision doc, brief, retro, board report,
                          # approvals, org chart, exec and hire agent files
  scripts/event.py        # appends one event to a day's events.jsonl
viewer/
  index.html              # meeting viewer
  serve.py                # serves the viewer plus a project's .boardroom/days
  demo/events.jsonl       # invented sample day for replay
docs/
```

**The target project (the company's state)**

```
.boardroom/
  board.md                # board-owned brief: goals, values, data, constraints
  approvals.md            # ledger of every board decision
  org.md                  # current staff, models, salaries, reporting lines
  days/YYYY-MM-DD/
    events.jsonl          # live event log the viewer reads
    am-meeting.transcript.md, am-meeting.md
    briefs/<lead>.md
    retros/<lead>.md
    pm-meeting.transcript.md, pm-meeting.md
    board-report.md
.claude/
  agents/<role>.md        # staff; model = pay grade, maxTurns = salary
  agent-memory/<role>/    # native per-agent memory
```

**Staff files have two parts.** A core block between `<!-- boardroom:core:<name> -->` markers holds the framework's role definition (from `templates/agents/core/`). Everything else belongs to the company: the frontmatter (pay grade and salary), project notes and remit. At the start of every work-day, `scripts/sync_agents.py` replaces each core block with the current version and leaves the rest alone. Updating the plugin therefore updates every company's staff the next time it works.

Project-specific instructions (the goal, what data exists, what the agents must never touch) go in the project's `.boardroom/board.md`. The framework only reads that file, so it never mentions any particular project.

## Org

**Execs:** CEO, CTO and CSO, created from templates on the first day.
- **CEO** chairs meetings, owns the call on "done" and writes decision docs and the board report.
- **CTO** owns engineering and data.
- **CSO** owns strategy and research, and has an explicit mandate to **block** work or a decision.

Further execs (CFO, marketing and so on) come through a board-approved org change.

**Headcount limits.** Within these, no board approval is needed:

```
exec
└── 1 lead
    ├── up to 2 seniors
    │   └── up to 2 juniors each
```

Anything beyond them goes in the board report as an org-change request. Approved extensions are recorded in `approvals.md`, and the skill honours them.

Day 1 starts at the bottom of the limits. The limits are ceilings, not targets ([research.md](research.md)).

**Pay grade and salary**
- Pay grade = `model:` in the agent file: opus for leads, sonnet for seniors, haiku or sonnet for juniors.
- Salary = `maxTurns`: 40 for a lead, 30 for a senior, 20 for a junior, unless a board-approved raise is in `approvals.md`.
- Token and tool use per agent are recorded in the event log and the board report.

## The day (`/work-day`)

The skill runs in the main session as the **secretary**. It spawns every agent, keeps the record and is the only one who talks to the board, but it makes no company decisions itself.

**One work-day is one real day.** The session stays open. After the morning meeting the company loops through work and check-ins until 17:00 local time or until the daily budget is spent. The budget is a share of the plan's weekly limit, 20% unless `board.md` says otherwise, read live from the app's usage data. The reason: a day of agent work takes about 20 minutes, but the evidence the company needs (users, replies, the board's answers) arrives on calendar time. Running days back to back gets ahead of the evidence and leaves execs with nothing real to do.

1. **Prepare.** If today's folder exists, the board chooses to continue it or restart as `<date>-2` (then `-3`…), so reports never collide. Check that `.boardroom/board.md` exists; if not, create it from the template and stop so the board can fill it in. Create the other state files and the execs if missing. Read yesterday's board report and the board's answers.
2. **Morning C-suite meeting.** Independent positions first (written in parallel, without seeing each other), then up to **10 rounds**.
   - Each round the CEO and CTO reply in parallel, then the CSO replies having seen their replies, so it never blocks a proposal that's already been dropped. A reply is one contribution, `PASS`, a `BLOCK:` or `LIFT:` from the CSO, or `CLOSE:` from the CEO.
   - The meeting ends on CLOSE with no active block, a round of all PASS, or after round 10.
   - The CEO writes the decision doc and one task brief per lead.
3. **Staffing** within the limits.
4. **Work.** All leads run in parallel, each in its own worktree and on its own branch.
   - Leads may delegate to and hire their own seniors and juniors, and log those events themselves.
   - Monitoring means verifying (tests, evidence), not reading over shoulders.
   - Leads never merge.
5. **Check-ins (the loop).** When a cycle's leads have returned, the C-suite holds a check-in of at most 3 rounds with no positions step. It looks at the results, the board's answers and the time and budget left. It then either briefs the next piece of work (back to step 3) or waits, re-checking in about an hour or when the board sends a message. At 17:00 or when the budget is spent, the loop ends.
   - **Board questions don't stop the day.** A lead that needs approval stops and says so. The secretary posts the question in chat, records it in `pending.md`, and work that doesn't depend on it carries on. The board answers whenever it likes, and the next check-in acts on the answer.
6. **Team retro.** Everyone below the C-suite who worked today writes one retro together.
7. **Evening C-suite meeting.** Same format. The CEO writes the board report.
**At any point,** the board can send a directive to a named exec. The secretary logs it, has the exec answer between steps, and brings the answer straight to the board.

8. **Close.** The secretary presents the report and asks each decision it needs, records the answers in `approvals.md`, and ends the day.

## Decision docs

Templates are in `skills/work-day/templates/`.
- **Meeting decision doc:** meeting goal · positions · decisions (what, owner, why) · blocks · briefs issued · questions for the board.
- **Task brief:** objective · goal it serves · definition of done (how it's verified) · output · boundaries · turn budget.
- **Retro:** done (with evidence) · not done and why · cost · learned · requests.
- **Board report:** summary · progress against goals · decisions needed (options plus a recommendation) · org-change requests · cost per agent.

## Meeting viewer

`viewer/index.html` shows a work-day live: the org chart with working indicators, meetings round by round with blocks highlighted, decisions, and an activity feed with requests waiting on the board. It polls `.boardroom/days/<day>/events.jsonl` every 2 seconds.

```bash
python3 <boardroom>/viewer/serve.py <project dir>
```

Then open `http://127.0.0.1:8787/?day=YYYY-MM-DD`, or `http://127.0.0.1:8787/` for the invented sample day.

**Event format:** one JSON object per line, each with `t` (ISO time) and `type`.

| type | fields |
|---|---|
| `day_start` / `day_end` | none |
| `hire` | `who`, `title`, `reports_to` (`board` for execs), `model`, `max_turns` |
| `meeting_start` | `id`, `title`, `max_rounds` |
| `position` | `meeting`, `who`, `text` |
| `say` / `block` / `unblock` | `meeting`, `round`, `who`, `text` |
| `meeting_end` | `meeting`, `decisions` (list), `doc` |
| `agent_start` | `who`, `task` |
| `agent_end` | `who`, `status` (`done` / `blocked`), `turns`, `tokens`, `summary` |
| `approval_request` | `id`, `who`, `text` |
| `approval_answer` | `id`, `answer` |
| `board_directive` | `id`, `to`, `text` (the board's words) |
| `directive_answer` | `id`, `who`, `text` |
| `retro` | `who`, `text` |
| `board_report` | `path`, `text` |
| `usage` | `five_hour`, `weekly` (percent of each plan limit used) |
| `wait` | `until` (HH:MM), `reason` |

## How we'll know it's working

- **PRs merged without changes per day.** This is the main output signal.
- **Tokens and tool uses per merged PR, per agent.** Each layer has to earn its place.
- **Board decisions raised vs. answered vs. overturned.** This tells us whether the approval gates sit in the right places.
- **Per real-time day:** cycles run, waits and their reasons, board questions with time from asked to answered, and weekly-limit percentage used (from `usage`, `wait`, `meeting_start` and `approval_*` events). If most check-ins end in a wait, the company is waiting on evidence, not on engineering, and the CSO's research should be driving the briefs.

All of this comes from git and the GitHub API, `events.jsonl` and `approvals.md`. After about 5 work-days we'll know whether the C-suite layer pays for itself. If merged output is near zero, we cut layers before adding any.

## Left out for now

- **Hooks that log subagents automatically.** Leads log their own reports' events instead.
- **Picking the latest day automatically in the viewer.** For now the URL takes `?day=`.
- **Committing a day's `.boardroom/` files in the target repo.** The board decides that.
- **Running two work-days at once.** A restart makes a new run of the date (`<date>-2`, `-3`); runs never overlap.
- **Running a day without the desktop app's usage data.** In the plain CLI the budget can't be read, so the day runs on the clock alone.
