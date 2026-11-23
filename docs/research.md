# Research notes

Gathered 2026-11-23 to learn from prior art. We are building our own, not adopting any of these. Items marked *unverified* were not confirmed from a primary source.

## Claude Code capabilities (from code.claude.com docs)

Sources: [sub-agents](https://code.claude.com/docs/en/sub-agents.md), [agent-teams](https://code.claude.com/docs/en/agent-teams.md), [costs](https://code.claude.com/docs/en/costs.md), [monitoring-usage](https://code.claude.com/docs/en/monitoring-usage.md).

| Question | Answer |
|---|---|
| Can subagents spawn subagents? | Yes, up to **3 layers** below the main conversation by default. Change it with `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`. |
| Is a new `.claude/agents/*.md` file usable mid-session? | Usually yes. The directory is watched, and the next delegation uses the new file. Restart if the agent isn't found. |
| Per-call model override? | Yes. The Agent tool takes `model` as an alias (opus/sonnet/haiku). There's no per-call system prompt; role text comes from the agent file or goes in the task message. |
| Per-agent token cap? | None. The only per-agent limit is `maxTurns`. `--max-budget-usd` applies to the whole session. |
| Per-agent usage after the fact? | Yes. Each subagent's transcript is saved at `~/.claude/projects/{project}/{sessionId}/subagents/agent-{agentId}.jsonl`. SubagentStart/SubagentStop hooks exist, and OTel events carry `agent_id` and `parent_agent_id`. |
| Native agent memory? | Yes. Frontmatter `memory: project` uses `.claude/agent-memory/<name>/MEMORY.md`; the first 200 lines or 25KB are loaded into the agent's prompt. |
| Can a subagent ask the human a question? | No. AskUserQuestion is removed from all subagents, so only the main thread can ask. |
| Agent teams? | Experimental, off by default, interactive sessions only, no nesting, one team per session. Not used. |

## Prior art

**Paperclip** ([repo](https://github.com/paperclipai/paperclip), MIT, March 2026). An orchestrator for agents running in Claude Code, Codex and others.
- Budgets are set per company, agent and project, with hard stops. Enforcement uses recorded spend, so work already running can overshoot.
- Agents wake on events (assignment, message, schedule), not by polling. Each task has exactly one locked assignee. "A mention alone does not assign work."
- The board approves hires and can pause or terminate agents. Config changes are versioned.
- No measured outcomes or postmortems were found. Self-organisation and org learning are on its roadmap as "not started".

**Anthropic Project Vend, phase 2** ([post](https://www.anthropic.com/research/project-vend-2)). Claude ran a shop, with a CEO agent added in phase 2.
- The CEO approved lenient requests about 8× more often than it denied them. Anthropic concluded the management layer added little.
- Same-model supervision shared the same blind spots.
- Two agents chatting overnight drifted into nonsense, and they nearly signed an illegal contract until a human caught it.
- What worked was forced procedure (look up the price before quoting), ledgers and tools, and narrow specialist roles: "bureaucracy matters".

**ChatDev** ([paper](https://arxiv.org/abs/2307.07924)). A simulated software company.
- Paired instructor/assistant chats, capped at **10 rounds** or 2 unchanged revisions.
- Having the assistant ask for specifics before answering helped (quality 0.395 vs 0.309 without). Removing roles hurt most (executability 0.88 → 0.58).

**MetaGPT** ([paper](https://arxiv.org/abs/2308.00352)). A team of PM, architect, engineer and QA.
- Agents exchange **structured documents through a shared pool instead of free chat**, and each starts only when its inputs arrive.
- It beat ChatDev: human revision cost 0.83 vs 2.5. Feedback from actually running the code was a big part of that.
- Adding roles raised quality, but cost rose about 50% going from 1 agent to 4.

## Failure-mode research

- **MAST** ([paper](https://arxiv.org/abs/2503.13657)) analysed 1,642 traces, with failure rates of 41–87%. Top failures were repeated steps, not knowing when to stop, ignoring the spec and weak verification. Most traced to system design. A final verification step gave +15.6%; a single owner of "done" gave +9.4%.
- **Conformity** ([1](https://arxiv.org/abs/2509.23055), [2](https://arxiv.org/html/2509.05396v2), [3](https://arxiv.org/html/2506.01332v1); abstracts only). Debating agents adopt the majority view up to 85% of the time, and one strong agent sways the rest.
- **Google, scaling agent systems** ([post](https://research.google/blog/towards-a-science-of-scaling-agent-systems-when-and-why-agent-systems-work/)). Multi-agent gave +81% on parallel tasks but was 39–70% worse on sequential ones. Independent agents amplified errors up to 17×; a central checker kept it to about 4×.
- **Anthropic's multi-agent research system** ([post](https://www.anthropic.com/engineering/multi-agent-research-system)). Multi-agent used about 15× the tokens of chat. An Opus lead with Sonnet workers beat Opus alone by 90%. Early versions spawned 50 subagents for simple queries. It's a poor fit for tightly coupled work, including most coding. Every delegation needs an objective, output format, tools and boundaries.

## Lessons we're taking

1. Hand off structured documents, not conversation.
2. Don't rely on same-model oversight. Use hard checks (tests, data) and the human board.
3. Every loop gets a stop rule, a verifier and one owner of "done".
4. Each layer of hierarchy multiplies cost and has no proven payoff. Start small and grow only where the work splits into parallel parts.
5. Procedure and tools beat management. Measure cost per accepted output for each agent.
