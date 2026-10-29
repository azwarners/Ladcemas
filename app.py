"""Ladcemas-Lite: a read-only launcher for Aggregare deployment reports."""

from __future__ import annotations

import os
from pathlib import Path
import re
from urllib.parse import urlsplit, urlunsplit

REPORT_PATH = Path(os.environ.get("AGGREGARE_REPORT_PATH", "/var/lib/aggregare/deployment-report.md"))
URL_RE = re.compile(r"https?://[^\s)]+", re.IGNORECASE)
INSTALLED_STATES = {"running", "installed"}
NON_LAUNCHER_APPS = {"apmatia", "ysparr"}
HEALTH_CHECK_PATHS = {"/health", "/actuator/health", "/api/v1/info"}


def valid_http_url(value: str) -> bool:
    try:
        parsed = urlsplit(value)
        return (
            parsed.scheme.lower() in {"http", "https"}
            and bool(parsed.hostname)
            and parsed.username is None
            and parsed.password is None
            and not parsed.query
            and not parsed.fragment
        )
    except ValueError:
        return False


def launcher_url(value: str) -> str:
    """Turn known health-check endpoints into the application's web root."""
    if not valid_http_url(value):
        return ""
    parsed = urlsplit(value)
    if parsed.path.rstrip("/") in HEALTH_CHECK_PATHS:
        return urlunsplit((parsed.scheme, parsed.netloc, "/", "", ""))
    return value


def parse_report(report: str) -> list[dict[str, str]]:
    """Extract installed applications and their recorded HTTP(S) endpoints."""
    apps: list[dict[str, str]] = []
    in_app_section = False
    current: dict[str, str] | None = None

    def save_current() -> None:
        if current and current.get("installed") == "yes" and current.get("url"):
            if current["name"].strip().casefold() not in NON_LAUNCHER_APPS:
                apps.append({"name": current["name"], "url": current["url"]})

    for line in report.splitlines():
        if line.startswith("## "):
            save_current()
            current = None
            in_app_section = line.strip() == "## Applications"
            continue
        if not in_app_section:
            continue
        if line.startswith("### "):
            save_current()
            current = {"name": line[4:].strip(), "installed": "no", "url": ""}
            continue
        if current is None:
            continue

        status = re.match(r"- Status: (.+)", line)
        if status:
            detail = status.group(1).lower()
            if "installed service detected" in detail:
                current["installed"] = "yes"
            else:
                state = re.search(r"recorded state:\s*([a-z_-]+)", detail)
                if state and state.group(1) in INSTALLED_STATES and "failed during" not in detail:
                    current["installed"] = "yes"

        if current["installed"] == "yes" and not current["url"] and line.startswith(("- Configured endpoint:", "- Endpoint recorded by last application check:")):
            match = URL_RE.search(line)
            if match and valid_http_url(match.group(0)):
                current["url"] = launcher_url(match.group(0))

    save_current()
    return apps


def create_app(report_path: Path | str | None = None) -> Flask:
    from flask import Flask, render_template

    app = Flask(__name__)
    source = Path(report_path) if report_path is not None else REPORT_PATH

    @app.get("/")
    def index():
        try:
            applications = parse_report(source.read_text(encoding="utf-8"))
            message = "No installed applications with a usable web address were found." if not applications else ""
        except (OSError, UnicodeError):
            applications = []
            message = "The Aggregare deployment report is not available yet. Run the Aggregare installer to generate it."
        return render_template("index.html", applications=applications, message=message)

    return app


if __name__ == "__main__":
    create_app().run(
        host=os.environ.get("LADCEMAS_HOST", "127.0.0.1"),
        port=int(os.environ.get("LADCEMAS_PORT", "5000")),
    )
