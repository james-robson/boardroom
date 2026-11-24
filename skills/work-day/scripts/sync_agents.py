#!/usr/bin/env python3
"""Bring a project's Boardroom staff files up to date with this version of Boardroom.

Usage: sync_agents.py <project dir>

Each staff file in <project>/.claude/agents/ has two parts:
  - a Boardroom-managed core block between
        <!-- boardroom:core:<name> ... -->  and  <!-- /boardroom:core -->
    which this script replaces with templates/agents/core/<name>.md
  - everything else (frontmatter = pay grade and salary, project notes, remit),
    which belongs to the company and is never touched.

Missing exec files (ceo, cto, cso) are created from templates/agents/<exec>.md.
Files without a core block are left alone and listed.
"""
import re
import sys
from pathlib import Path

TEMPLATES = Path(__file__).resolve().parent.parent / "templates" / "agents"
EXECS = ("ceo", "cto", "cso")
BLOCK = re.compile(r"(<!-- boardroom:core:([a-z0-9-]+)[^\n]*-->\n)(.*?)(<!-- /boardroom:core -->)", re.S)

if len(sys.argv) != 2:
    sys.exit(__doc__)
agents = Path(sys.argv[1]).resolve() / ".claude" / "agents"
agents.mkdir(parents=True, exist_ok=True)


def fill(match):
    core = TEMPLATES / "core" / f"{match.group(2)}.md"
    if not core.exists():
        sys.exit(f"no core definition for {match.group(2)!r} ({core})")
    return match.group(1) + core.read_text().strip() + "\n" + match.group(4)


created, updated, unchanged, skipped = [], [], [], []
for name in EXECS:
    path = agents / f"{name}.md"
    if not path.exists():
        path.write_text((TEMPLATES / f"{name}.md").read_text())
        created.append(name)

for path in sorted(agents.glob("*.md")):
    text = path.read_text()
    if not BLOCK.search(text):
        skipped.append(path.stem)
        continue
    new = BLOCK.sub(fill, text)
    if new != text:
        path.write_text(new)
        if path.stem not in created:
            updated.append(path.stem)
    elif path.stem not in created:
        unchanged.append(path.stem)

for label, names in (("created", created), ("updated", updated), ("unchanged", unchanged),
                     ("skipped, no core block", skipped)):
    if names:
        print(f"{label}: {', '.join(names)}")
