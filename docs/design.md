# Boardroom — draft design

Status: **draft for board review**. Nothing here is built yet. Background is in [origin-conversation.md](origin-conversation.md) and [research.md](research.md).

## The rule

Agents propose and build. The board (the human) approves anything that ships, spends money, goes public or changes the org beyond its limits.

## Org

**Day 1 execs:** CEO, CTO, CSO.
- **CEO** chairs meetings, owns the call on "done" and writes the board report.
- **CTO** owns engineering.
- **CSO** owns strategy and research, and has an explicit mandate to **block** work or a decision. Blocks and the reasons for them go into the meeting's decision doc.

CFO and marketing come later, through a board-approved org change.

**Headcount limits per exec.** Execs may move within these without asking the board:

```
exec
└── 1 lead
    ├── up to 2 seniors
    │   └── up to 2 juniors each
```

Anything beyond that, or any new exec, goes in the board report as an org-change request.

**Start at the bottom of the limits.** Day 1 is one lead per exec at most, and no seniors or juniors until a retro shows the work splits into parallel parts. The limits are ceilings, not targets: research shows each layer multiplies token cost with no proven payoff ([research.md](research.md)).

**Pay grade and salary**
- Pay grade = `model:` in the agent file. Opus for leads; Sonnet or Haiku below.
- Salary = `maxTurns` in the agent file. A raise means more turns, approved by the board. Claude Code has no per-agent token cap, so turns are the hard limit and tokens are reported.

## The day (`/work-day`)

The skill runs in the main session. It does **all the spawning itself**: execs decide, and the skill acts on their decisions. This keeps lead → senior → junior within Claude Code's default limit of 3 nested layers, and means the main thread is the only place that can ask the board a question.

1. **Read the room.** The skill loads `board/goals.md`, `board/approvals.md`, `org/chart.md`, yesterday's board report, and the board's answers to its decisions.
2. **Morning C-suite meeting**
   - Each exec first writes an **independent position**, without seeing the others' (this counters conformity).
   - Then up to **10 rounds** of discussion, one contribution per exec per round. The meeting ends early once a round changes nothing.
   - The CEO closes it with a **decision doc** (template below). The CSO can block.
3. **Staffing.** Within the limits, the skill writes or updates `.claude/agents/<role>.md`: role description, `model:`, `maxTurns:`, `memory: project`.
4. **Work**
   - Each lead gets a **task brief** (template below) and may delegate to its seniors and juniors.
   - Every task has exactly one owner and its own branch or worktree in the target repo.
   - "Monitoring" means **verifying**: run the tests, check the diff against the brief, check the evidence. It doesn't mean reading over shoulders.
5. **Retros.** Each lead writes a retro: what was done, evidence, cost, what blocked them, and requests.
6. **Evening C-suite meeting.** Same format as the morning. Its output is the **board report**.
7. **Mid-day approvals.** If an exec needs a decision that can't wait, the skill asks the board directly. Anything that can wait goes in the board report. Every answer is recorded in `board/approvals.md`.

## Decision docs

Every meeting and handoff produces a fixed-format document, not a transcript, so the next step reads structure rather than chat. A meeting transcript is still saved alongside it (for the UI and for audit), but nothing downstream relies on it.

**Meeting decision doc:** goal of the meeting · positions (one line per exec) · decisions (what, owner, why) · blocks (who, why, resolved?) · task briefs issued · open questions for the board.

**Task brief:** objective · why it matters (link to a goal) · definition of done (how it will be verified) · output format and location · boundaries (what not to touch, what needs approval) · turn budget.

**Retro:** done (with evidence links) · not done and why · cost (turns, tokens) · what we learned · requests (hires, raises, access).

**Board report:** summary in 5 lines or fewer · progress against goals · **decisions needed** (each with options and the C-suite's recommendation) · **org-change requests** · cost (per agent: turns, tokens, merged PRs).

## Folder layout

```
board/
  goals.md              # board-owned: goals and values
  approvals.md          # ledger of every board decision
org/
  chart.md              # current headcount, models, salaries
  days/YYYY-MM-DD/
    events.jsonl        # live event log the viewer reads
    am-meeting.md       # decision doc (+ am-meeting.transcript.md)
    briefs/<role>.md
    retros/<lead>.md
    pm-meeting.md
    board-report.md
.claude/
  agents/<role>.md      # hires; model = pay grade, maxTurns = salary
  agent-memory/<role>/  # native per-agent memory, committed
  skills/work-day/SKILL.md
viewer/
  index.html            # meeting viewer (reads events.jsonl)
  demo/events.jsonl     # sample day for replay
```

The target project (Push Realm first) lives in its own repo. Agents change it only through branches and PRs, and PRs wait for board approval before merge.

## Guardrails

- Push Realm's MCP tools publish immediately with no preview, so they are **denied in settings**, not just discouraged in prompts. Any public action goes through the board.
- No merges, spending, public posts or credential changes without a board approval in the ledger.

## How we'll know it's working

- **Merged-without-changes PRs per day.** This is the main output signal.
- **Tokens and turns per merged PR, per agent.** Each layer has to earn its place.
- **Board decisions raised vs. answered vs. overturned.** This tells us whether the approval gates sit in the right places.

All of this comes from git and the GitHub API, the saved transcripts, and `board/approvals.md`. After about 5 work-days we'll know whether the C-suite layer pays for itself. If merged output is near zero, we cut layers before adding any.

## Open questions

- None blocking day 1.

## Usage data (board answer, 2026-11-23)

- Push Realm has **data-fetching scripts** that partly answer the usage questions. The engineering team starts from those and works out whether it needs to add more.
- Any new monitoring or access (for example Railway) is a **board request**: it goes in the board report or a mid-day approval. Agents don't get it by default.

## Meeting viewer

A read-only page in `viewer/index.html` that shows a work-day live:
- the org chart, with a working indicator on each agent
- meetings in progress, round by round, with blocks highlighted
- the decisions each meeting reached
- an activity feed, including requests waiting on the board

It reads one file: `org/days/YYYY-MM-DD/events.jsonl`. The `/work-day` skill appends to that file as the day runs, and the page polls it every 2 seconds.

**Event format:** one JSON object per line, each with `t` (ISO time) and `type`. The other fields depend on the type:

| type | fields |
|---|---|
| `day_start` / `day_end` | none |
| `hire` | `who`, `title`, `reports_to` (`board` for execs), `model`, `max_turns` |
| `meeting_start` | `id`, `title`, `max_rounds` |
| `position` | `meeting`, `who`, `text` (independent position) |
| `say` | `meeting`, `round`, `who`, `text` |
| `block` | `meeting`, `who`, `text` |
| `unblock` | `meeting`, `who`, `text` |
| `meeting_end` | `meeting`, `decisions` (list of strings), `doc` (path) |
| `agent_start` | `who`, `task` |
| `agent_end` | `who`, `status` (`done` / `blocked`), `turns`, `summary` |
| `approval_request` | `id`, `who`, `text` |
| `approval_answer` | `id`, `answer` |
| `retro` | `who`, `text` |
| `board_report` | `path`, `text` |

**Run it:** serve the repo root (`python3 -m http.server 8787`), then open:
- `http://localhost:8787/viewer/?day=YYYY-MM-DD` for a real day
- `http://localhost:8787/viewer/` for a replay of the sample day in `viewer/demo/events.jsonl` (sample data, not a real day)

**Left out for now:**
- Agents writing their own events. Only the skill writes events, so seniors and juniors spawned *by a lead* don't show a working indicator unless the lead logs them. If that turns out to matter, the SubagentStart/SubagentStop hooks could write those events automatically.
- Websockets or a server, editing, and history across days.
