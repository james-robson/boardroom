# Boardroom — origin conversation

Saved from the planning chat that started this project (2026-11-23). Nothing has been built yet; this is the brief for the first session in this repo.

## The idea

A company made of AI agents, run inside Claude Code, that works on a target project. The human owner is **the board**.

- **C-suite agents**: CEO, CTO, CSO, CFO, etc. Each decides which roles it wants beneath it (devs, QA, product, marketing...).
- **HR agent**: for each hire, picks a suitable model as the "pay grade" (e.g. lead dev → Opus, regular dev → Sonnet, junior → Haiku), writes the role description, and stands up a **permanent, memory-driven agent** for that role.
- **`/work-day` skill**:
  1. C-suite review how the project is going and the requirements.
  2. They decide who to hire (or not) and hand high-level tasks to each department.
  3. HR hires/configures the agents.
  4. Departments do the work.
  5. During the day the C-suite can ask the board for approvals — more salary (token budget) for an agent, software licences, etc. When the board approves, it's actioned.
  6. At the end of the day the board gets a summary.

## Prior art (from memory, not yet researched)

- **ChatDev** (2023) — simulated software company (CEO, CTO, programmer, reviewer, tester). Fixed org, single run.
- **MetaGPT** (2023) — PM, architect, engineer, QA following SOPs. Fixed team, no persistence.
- **CrewAI / AutoGen** — role-based multi-agent frameworks (building blocks).
- **Paperclip** (2026) — open-source "zero-human company" orchestrator: org charts, CEO agent, per-agent budgets, heartbeats, human board approvals. Closest match — review before building.
- **Anthropic's Project Vend** — Claude ran a real vending business, later with a "CEO" agent. Good reading on how agent hierarchies behave and fail.

What's distinctive here: model choice as pay grade, tokens as salary with board-approved raises, a C-suite that changes headcount day to day, and it runs on a real repo in Claude Code.

## How it maps onto Claude Code

| Company concept | Claude Code mechanism |
|---|---|
| Hiring an employee | HR writes `.claude/agents/<role>.md`; `model:` frontmatter = pay grade, body = role description |
| Permanent memory | A memory file per employee committed to the repo (e.g. `org/staff/<role>/memory.md`) — cloud containers are wiped between sessions |
| `/work-day` | A skill in `.claude/skills/work-day/` that runs the C-suite meeting, hiring, task assignment, end-of-day summary |
| Board approvals | Questions to the human mid-session; an approvals ledger file so later days honour past decisions |
| Daily summary | A dated file, e.g. `org/days/YYYY-MM-DD.md` |

## Risks to design against

- **Management overhead** — C-suite chatter can cost more tokens than the work. Keep meetings short and structured.
- **Agents agree with each other** — a hierarchy doesn't create dissent. Give someone (QA / CSO) an explicit mandate to block work.
- **Headcount creep** — hard daily token budget, or the C-suite keeps hiring.

## Decisions made

- **Standalone, not branded** to any one product. Repo name: `boardroom`.
- **Separate repo** from the projects it works on: this repo is "the company" (agents, skills, memories, ledger, summaries); a target project is "the workplace", attached per session and changed via branches/PRs. Avoid git submodules.
- **First target project**: Push Realm. What the agents can realistically do there:
  - Engineering / QA / product: fully — read, write, test, push branches, open PRs. PRs wait for board approval before merge.
  - Marketing: draft copy/docs/changelogs; anything public needs board approval.
  - Ops / finance: limited to whatever credentials and connectors the environment has.
  - Push Realm's own MCP tools publish immediately with no preview — strict rule or board sign-off required.
- **Guiding rule**: agents propose and build; the board approves anything that ships, spends money, or goes public.

## Next step

In a fresh session in this repo: draft the folder layout and the `/work-day` flow for the board to review **before** building anything.
