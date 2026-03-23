#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse


def _split_links(raw: str) -> list[tuple[str, str]]:
    links: list[tuple[str, str]] = []
    for item in raw.split(";"):
        item = item.strip()
        if not item:
            continue
        if "|" in item:
            label, url = item.split("|", 1)
        else:
            label, url = item, item
        links.append((label.strip(), url.strip()))
    return links


class Handler(BaseHTTPRequestHandler):
    server_version = "NeuralHouseScaffold/1.0"

    def _write(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args) -> None:  # noqa: A003
        return

    def do_GET(self) -> None:  # noqa: N802
        service_name = os.environ.get("SERVICE_NAME", "service")
        service_mode = os.environ.get("SERVICE_MODE", "json")
        service_message = os.environ.get("SERVICE_MESSAGE", "Scaffold service is running.")
        service_links = _split_links(os.environ.get("SERVICE_LINKS", ""))

        parsed = urlparse(self.path)
        if parsed.path in {"/healthz", "/readyz"}:
            body = json.dumps({"status": "ok", "service": service_name}).encode("utf-8")
            self._write(200, body, "application/json")
            return

        if service_mode == "html":
            links_html = "".join(
                f'<li><a href="{html.escape(url)}">{html.escape(label)}</a></li>'
                for label, url in service_links
            )
            body = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{html.escape(service_name)}</title>
    <style>
      :root {{
        color-scheme: light;
        font-family: Inter, ui-sans-serif, system-ui, sans-serif;
        background: linear-gradient(180deg, #f7f4ee 0%, #eef3f8 100%);
      }}
      body {{
        margin: 0;
        min-height: 100vh;
        display: grid;
        place-items: center;
        color: #132238;
      }}
      main {{
        max-width: 720px;
        margin: 24px;
        padding: 32px;
        border-radius: 24px;
        background: rgba(255, 255, 255, 0.82);
        box-shadow: 0 24px 60px rgba(15, 23, 42, 0.12);
        backdrop-filter: blur(12px);
      }}
      h1 {{ margin-top: 0; font-size: 3rem; line-height: 1; }}
      p, li {{ font-size: 1.05rem; line-height: 1.6; }}
      a {{ color: #0f62fe; }}
    </style>
  </head>
  <body>
    <main>
      <p>{html.escape(service_name)}</p>
      <h1>Scaffold ready</h1>
      <p>{html.escape(service_message)}</p>
      <ul>{links_html}</ul>
    </main>
  </body>
</html>""".encode("utf-8")
            self._write(200, body, "text/html; charset=utf-8")
            return

        body = json.dumps(
            {
                "service": service_name,
                "message": service_message,
                "links": service_links,
            }
        ).encode("utf-8")
        self._write(200, body, "application/json")


def main() -> None:
    port = int(os.environ.get("SERVICE_PORT", "8080"))
    server = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    print(f"{os.environ.get('SERVICE_NAME', 'service')} listening on {port}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()

