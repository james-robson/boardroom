#!/usr/bin/env python3
"""Serve the Boardroom viewer for a project.

Usage: python3 serve.py <project dir> [port]

Serves this folder at / and <project>/.boardroom/days/ at /days/, on 127.0.0.1.
Then open http://127.0.0.1:<port>/?day=YYYY-MM-DD (or / for the sample replay).

POST /wake?day=<day> appends a `wake` event to that day's events.jsonl, which ends
the secretary's wait early (the viewer's "Continue now" button).
"""
import http.server
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlsplit

VIEWER = Path(__file__).resolve().parent
if len(sys.argv) < 2:
    sys.exit(__doc__)
DAY_NAME = re.compile(r"\d{4}-\d{2}-\d{2}(-\d+)?")
DAYS = (Path(sys.argv[1]) / ".boardroom" / "days").resolve()
PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 8787


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if urlsplit(self.path).path == "/days.json":
            days = sorted((d.name for d in DAYS.iterdir()
                           if DAY_NAME.fullmatch(d.name) and (d / "events.jsonl").exists()),
                          reverse=True) if DAYS.is_dir() else []
            body = json.dumps(days).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        super().do_GET()

    def do_POST(self):
        url = urlsplit(self.path)
        day = parse_qs(url.query).get("day", [""])[0]
        log = DAYS / day / "events.jsonl"
        # the custom header makes a browser preflight cross-site posts, which this server never approves
        if url.path != "/wake" or self.headers.get("X-Boardroom") != "wake":
            self.send_error(404); return
        if not DAY_NAME.fullmatch(day) or not log.is_file():
            self.send_error(400, "unknown day"); return
        event = {"t": datetime.now(timezone.utc).isoformat(timespec="seconds"), "type": "wake", "who": "board"}
        with open(log, "a") as f:
            f.write(json.dumps(event) + "\n")
        self.send_response(204)
        self.end_headers()

    def translate_path(self, path):
        path = unquote(urlsplit(path).path)
        if path.startswith("/days/"):
            base, rest = DAYS, path[len("/days/"):]
        else:
            base, rest = VIEWER, path.lstrip("/")
        target = (base / rest).resolve()
        # refuse anything that escapes its base folder
        return str(target if target.is_relative_to(base) else base / "__missing__")

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, *args):
        pass


print(f"Boardroom viewer: http://127.0.0.1:{PORT}/  (days from {DAYS})")
http.server.ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
