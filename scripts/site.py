#!/usr/bin/env python3
"""Build, check and serve the LoongLab static website.

Architecture is modelled on REA's `scripts/website.py` (MIT, Copyright (c)
2026 morluto) -- authored HTML in `public/`, shared regions injected from
`templates/`, output generated into `_site/`. See THIRD_PARTY_NOTICES.md.
"""

from __future__ import annotations

import argparse
import http.server
import re
import shutil
import sys
from html.parser import HTMLParser
from pathlib import Path
from string import Template

ROOT = Path(__file__).resolve().parent.parent
PUBLIC = ROOT / "public"
TEMPLATES = ROOT / "templates"
OUT = ROOT / "_site"

# Public origin, used for the sitemap and canonical URLs.
SITE_ORIGIN = "https://loonglab.com"

# Region marker in a page -> template file whose rendered body replaces it.
REGIONS = {
    "site-header": "header.html.tmpl",
    "site-footer": "footer.html.tmpl",
}

SKIP_DIRS = {"__pycache__", ".venv", "node_modules", "_site"}


def rel_base(page: Path) -> str:
    """Relative prefix from a page to the site root (e.g. '../../')."""
    depth = len(page.parent.parts) if page.parent != Path(".") else 0
    return "../" * depth or "./"


def render_template(name: str, base: str) -> str:
    return Template((TEMPLATES / name).read_text("utf-8")).substitute(base=base)


def inject_regions(html: str, page: Path) -> str:
    base = rel_base(page)
    for region, template in REGIONS.items():
        begin = f"<!-- BEGIN:{region} -->"
        end = f"<!-- END:{region} -->"
        if html.count(begin) != 1 or html.count(end) != 1:
            raise SystemExit(f"{page}: expected exactly one {region} marker pair")
        body = render_template(template, base)
        html = re.sub(
            re.escape(begin) + r".*?" + re.escape(end),
            begin + "\n" + body + end,
            html,
            flags=re.DOTALL,
        )
    return html


def html_files(root: Path) -> list[Path]:
    return [
        path
        for path in sorted(root.rglob("*.html"))
        if not any(part in SKIP_DIRS or part.startswith(".") for part in path.relative_to(root).parts)
    ]


def build() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    for src in sorted(PUBLIC.rglob("*")):
        rel = src.relative_to(PUBLIC)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        dest = OUT / rel
        if src.is_dir():
            dest.mkdir(parents=True, exist_ok=True)
        elif src.suffix == ".html":
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(inject_regions(src.read_text("utf-8"), rel), "utf-8")
        else:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
    write_sitemap()
    print(f"Built {OUT.relative_to(ROOT)} ({len(html_files(OUT))} pages)")


def write_sitemap() -> None:
    routes = [
        "/" + str(path.relative_to(OUT).parent).replace(".", "").strip("/")
        for path in html_files(OUT)
        if path.name == "index.html"
    ]
    urls = "\n".join(
        f'  <url><loc>{SITE_ORIGIN}{"" if route == "/" else route + "/"}</loc></url>'
        for route in sorted(set(routes))
    )
    (OUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{urls}\n</urlset>\n",
        "utf-8",
    )


class MetaReader(HTMLParser):
    """Read title and description, and collect local link targets."""

    def __init__(self) -> None:
        super().__init__()
        self.in_title = False
        self.title = ""
        self.description = ""
        self.links: list[str] = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "title":
            self.in_title = True
        if tag == "meta" and (a.get("name") or "").lower() == "description":
            self.description = a.get("content") or ""
        for attr in ("href", "src"):
            value = a.get(attr)
            if value:
                self.links.append(value)

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False

    def handle_data(self, data):
        if self.in_title:
            self.title += data


def check() -> None:
    issues: list[str] = []
    for path in html_files(PUBLIC):
        rel = path.relative_to(PUBLIC)
        text = path.read_text("utf-8")
        for region in REGIONS:
            if text.count(f"<!-- BEGIN:{region} -->") != 1:
                issues.append(f"{rel}: missing or duplicated BEGIN:{region}")
            if text.count(f"<!-- END:{region} -->") != 1:
                issues.append(f"{rel}: missing or duplicated END:{region}")
        meta = MetaReader()
        meta.feed(text)
        if not meta.title.strip():
            issues.append(f"{rel}: missing <title>")
        if not meta.description.strip():
            issues.append(f"{rel}: missing meta description")
        for target in meta.links:
            if re.match(r"^(https?:|mailto:|#|data:)", target):
                continue
            local = target.split("#", 1)[0].split("?", 1)[0]
            if not local:
                continue
            resolved = (path.parent / local).resolve()
            if not resolved.exists():
                issues.append(f"{rel}: broken link {target}")
    if issues:
        raise SystemExit("Website check failed:\n- " + "\n- ".join(issues))
    print(f"Checked {len(html_files(PUBLIC))} pages: OK")


def serve(host: str, port: int) -> None:
    if not OUT.exists():
        build()
    handler = lambda *a, **k: http.server.SimpleHTTPRequestHandler(*a, directory=str(OUT), **k)
    with http.server.ThreadingHTTPServer((host, port), handler) as httpd:
        shown = "localhost" if host in ("0.0.0.0", "::") else host
        print(f"Serving http://{shown}:{port}/ (bound to {host}, Ctrl-C to stop)")
        httpd.serve_forever()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("build")
    sub.add_parser("check")
    serve_parser = sub.add_parser("serve")
    serve_parser.add_argument("--port", type=int, default=4173)
    serve_parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Interface to bind (use 0.0.0.0 to reach it from outside WSL).",
    )
    sub.add_parser("deploy-check")
    args = parser.parse_args()

    if args.command == "build":
        build()
    elif args.command == "check":
        check()
    elif args.command == "serve":
        serve(args.host, args.port)
    elif args.command == "deploy-check":
        check()
        build()


if __name__ == "__main__":
    main()
