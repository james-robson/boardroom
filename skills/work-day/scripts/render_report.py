#!/usr/bin/env python3
"""Render a day's board-report.md to a readable, self-contained board-report.html beside it.

Usage: render_report.py <path/to/board-report.md>

No dependencies. Handles the markdown the report template uses: headings, paragraphs,
nested bullet/numbered lists, tables, bold/italic, inline code, code blocks, links.
Links to other .md files in the day folder stay relative, so they open next to the report.
"""
import html
import re
import sys
from pathlib import Path

CSS = """
:root{--bg:#f5f4f0;--panel:#fff;--ink:#1d1d1f;--muted:#6b6b70;--line:#e4e2dc;--accent:#7a4fd1;--code:#f0eee8}
@media (prefers-color-scheme:dark){:root{--bg:#121215;--panel:#1b1b1f;--ink:#ececf0;--muted:#9a9aa3;--line:#2d2d34;--accent:#a98bf0;--code:#26262b}}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif}
main{max-width:860px;margin:24px auto;padding:24px 32px;background:var(--panel);border:1px solid var(--line);border-radius:10px}
@media (max-width:700px){main{margin:0;border-radius:0;border-left:0;border-right:0;padding:16px}}
h1{font-size:24px;margin:0 0 16px}h2{font-size:18px;margin:28px 0 10px;padding-bottom:4px;border-bottom:1px solid var(--line)}h3{font-size:15px;margin:20px 0 8px}
p,li{margin:6px 0}ul,ol{padding-left:22px}a{color:var(--accent)}
code{font:13px ui-monospace,SFMono-Regular,Menlo,monospace;background:var(--code);padding:1px 5px;border-radius:4px}
pre{background:var(--code);padding:12px;border-radius:8px;overflow:auto}pre code{padding:0;background:none}
.table{overflow-x:auto;margin:10px 0}table{border-collapse:collapse;font-size:13.5px;width:100%}
th,td{border:1px solid var(--line);padding:6px 9px;text-align:left;vertical-align:top}th{background:var(--code)}
blockquote{margin:10px 0;padding:4px 12px;border-left:3px solid var(--line);color:var(--muted)}
"""

LIST = re.compile(r"^(\s*)([-*]|\d+\.)\s+(.*)")
BLOCK_START = re.compile(r"^(#{1,4}\s|```|\s*\||\s*([-*]|\d+\.)\s|>)")


def inline(s: str) -> str:
    codes = []

    def stash(m):
        codes.append(html.escape(m.group(1)))
        return f"\0{len(codes) - 1}\0"

    s = re.sub(r"`([^`]+)`", stash, s)
    s = html.escape(s, quote=True)

    def link(m):
        text, href = m.group(1), html.unescape(m.group(2))
        ext = ' target="_blank" rel="noopener"' if re.match(r"https?://", href) else ""
        return f'<a href="{html.escape(href, quote=True)}"{ext}>{text}</a>'

    s = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", link, s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(^|[\s(])\*([^*\s][^*]*)\*", r"\1<em>\2</em>", s)
    return re.sub(r"\0(\d+)\0", lambda m: f"<code>{codes[int(m.group(1))]}</code>", s)


def cells(row: str):
    return [c.strip() for c in row.strip().strip("|").split("|")]


def render(md: str) -> str:
    lines = md.replace("\r", "").split("\n")
    out, i = [], 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("```"):
            buf, i = [], i + 1
            while i < len(lines) and not lines[i].startswith("```"):
                buf.append(lines[i]); i += 1
            out.append(f"<pre><code>{html.escape(chr(10).join(buf))}</code></pre>"); i += 1
            continue
        if m := re.match(r"^(#{1,4})\s+(.*)", line):
            n = len(m.group(1)); out.append(f"<h{n}>{inline(m.group(2))}</h{n}>"); i += 1
            continue
        if re.match(r"^\s*\|", line) and i + 1 < len(lines) and re.match(r"^\s*\|?\s*:?-{3,}", lines[i + 1]):
            t = ["<div class=\"table\"><table><thead><tr>", *(f"<th>{inline(c)}</th>" for c in cells(line)), "</tr></thead><tbody>"]
            i += 2
            while i < len(lines) and re.match(r"^\s*\|", lines[i]):
                t += ["<tr>", *(f"<td>{inline(c)}</td>" for c in cells(lines[i])), "</tr>"]; i += 1
            out.append("".join(t) + "</tbody></table></div>")
            continue
        if LIST.match(line):
            stack, buf = [], []
            while i < len(lines) and (LIST.match(lines[i]) or (stack and re.match(r"^\s{2,}\S", lines[i]))):
                m = LIST.match(lines[i])
                if not m:
                    buf.append(" " + inline(lines[i].strip())); i += 1
                    continue
                ind, tag = len(m.group(1)), "ol" if m.group(2)[0].isdigit() else "ul"
                while stack and ind < stack[-1][0]:
                    buf.append(f"</li></{stack.pop()[1]}>")
                if not stack or ind > stack[-1][0]:
                    stack.append((ind, tag)); buf.append(f"<{tag}><li>")
                else:
                    buf.append("</li><li>")
                buf.append(inline(m.group(3))); i += 1
            while stack:
                buf.append(f"</li></{stack.pop()[1]}>")
            out.append("".join(buf))
            continue
        if line.startswith(">"):
            buf = []
            while i < len(lines) and lines[i].startswith(">"):
                buf.append(re.sub(r"^>\s?", "", lines[i])); i += 1
            out.append(f"<blockquote>{inline(' '.join(buf))}</blockquote>")
            continue
        if not line.strip():
            i += 1
            continue
        buf = []
        while i < len(lines) and lines[i].strip() and not BLOCK_START.match(lines[i]):
            buf.append(lines[i]); i += 1
        out.append(f"<p>{inline(' '.join(buf))}</p>")
    return "\n".join(out)


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    src = Path(sys.argv[1])
    md = src.read_text()
    title = next((l[2:].strip() for l in md.splitlines() if l.startswith("# ")), "Board report")
    page = (f"<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\">"
            f"<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
            f"<title>{html.escape(title)}</title><style>{CSS}</style></head>"
            f"<body><main>{render(md)}</main></body></html>\n")
    dst = src.with_suffix(".html")
    dst.write_text(page)
    print(dst)


if __name__ == "__main__":
    main()
