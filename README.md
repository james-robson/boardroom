# Boardroom

Run a company of AI agents on your project, inside Claude Code. You are **the board**.

Each work-day:
1. A C-suite (CEO, CTO, CSO) meets in a limited number of rounds and decides the plan.
2. They hire within fixed limits. The model is the pay grade and the turn budget is the salary.
3. Leads do the work on branches, delegating to seniors and juniors.
4. The leads write retros, the C-suite meets again, and you get a board report with the decisions you need to make.

Agents propose and build. You approve anything that ships, spends money, goes public or grows the org beyond its limits.

## Setup

1. Install the plugin, from a Claude Code session in any folder:
   ```
   /plugin marketplace add <path to this repo>
   /plugin install boardroom@boardroom
   ```
2. In your project, write `.boardroom/board.md`: the goal, values, what data exists and what agents must never do. The first `/work-day` creates a blank one from [the template](skills/work-day/templates/board.md) if it's missing.
3. Run `/boardroom:work-day` from a Claude Code session in your project.

## Watching a day

```bash
python3 <path to this repo>/viewer/serve.py <path to your project>
```

Then open `http://127.0.0.1:8787/?day=YYYY-MM-DD`, or `http://127.0.0.1:8787/` for an invented sample day.

## Where things live

All of a company's state lives in **your project**, not here:
- `.boardroom/`: the board brief, approvals ledger, org chart, and one folder per day
- `.claude/agents/`: the staff

This repo is only the framework. See [docs/design.md](docs/design.md) for how it works and [docs/research.md](docs/research.md) for the prior art behind it.
