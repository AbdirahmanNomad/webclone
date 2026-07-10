"""
webclone serve — Embedded replay server for offline clones.

Serves HTML, captured JSON, and mocks API endpoints from recorded responses.
Injects browser storage (localStorage/sessionStorage) for SPA bootstrapping.
"""

import http.server
import json
import os
import re
import socketserver
from pathlib import Path
from urllib.parse import urlparse


class ReplayHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP handler that replays recorded API responses and injects storage."""

    def __init__(self, *args, directory=None, **kwargs):
        self.clone_dir = directory or "."
        self.data_dir = os.path.join(self.clone_dir, "data")
        self.storage_file = os.path.join(self.clone_dir, "browser-storage.json")
        super().__init__(*args, directory=directory, **kwargs)

    def _try_data_file(self, path):
        """Try to serve from data/ directory for API routes."""
        # Normalize path to a filename
        fname = path.strip("/").replace("/", "_")
        fname = re.sub(r'[<>:"|?*]', '_', fname)[:100]
        candidates = [
            os.path.join(self.data_dir, fname + ".json"),
            os.path.join(self.data_dir, fname),
        ]
        for candidate in candidates:
            if os.path.isfile(candidate):
                return candidate
        return None

    def _inject_storage_script(self, html):
        """Inject browser storage restoration before app initialization."""
        storage_script = ""
        if os.path.isfile(self.storage_file):
            try:
                with open(self.storage_file) as f:
                    storage = json.load(f)
                ls = json.dumps(storage.get("localStorage", {}))
                ss = json.dumps(storage.get("sessionStorage", {}))
                cookies = json.dumps(storage.get("cookies", ""))
                storage_script = f"""
<script>
(function() {{
  try {{
    var _ls = {ls};
    var _ss = {ss};
    var _ck = {cookies};
    for (var k in _ls) {{ try {{ localStorage.setItem(k, _ls[k]); }} catch(e) {{}} }}
    for (var k in _ss) {{ try {{ sessionStorage.setItem(k, _ss[k]); }} catch(e) {{}} }}
    if (_ck) {{ try {{ document.cookie = _ck; }} catch(e) {{}} }}
  }} catch(e) {{}}
}})();
</script>"""
            except Exception:
                pass
        return html.replace("</head>", storage_script + "\n</head>", 1)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        # Try data/ replay first
        data_file = self._try_data_file(path)
        if data_file:
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            with open(data_file, "rb") as f:
                self.wfile.write(f.read())
            return

        # Serve HTML with storage injection
        if path == "/" or path.endswith(".html") or (not os.path.splitext(path)[1] and os.path.isdir(os.path.join(self.clone_dir, path.lstrip("/")))):
            filepath = os.path.join(self.clone_dir, path.lstrip("/") or "index.html")
            if os.path.isdir(filepath):
                filepath = os.path.join(filepath, "index.html")
            if os.path.isfile(filepath):
                self.send_response(200)
                ct = "text/html"
                if filepath.endswith(".css"):
                    ct = "text/css"
                elif filepath.endswith(".js"):
                    ct = "application/javascript"
                self.send_header("Content-Type", ct)
                self.end_headers()
                with open(filepath, "rb") as f:
                    content = f.read()
                if ct == "text/html":
                    content = self._inject_storage_script(content.decode("utf-8", errors="replace")).encode("utf-8")
                self.wfile.write(content)
                return

        # Fall back to static file serving
        super().do_GET()

    def do_POST(self):
        """Accept POST requests gracefully — return recorded response if available."""
        parsed = urlparse(self.path)
        data_file = self._try_data_file(parsed.path)
        if data_file:
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            with open(data_file, "rb") as f:
                self.wfile.write(f.read())
            return

        # Form emulation — return friendly offline message
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(b"""<!DOCTYPE html>
<html><body style="font-family:sans-serif;text-align:center;padding:50px;">
<h2>&#10003; Submitted!</h2>
<p>This form is offline. Your submission was recorded locally.</p>
</body></html>""")

    def log_message(self, format, *args):
        print(f"  {args[0]}")


def serve(clone_dir, port=8000):
    """Start the replay server."""
    clone_dir = os.path.abspath(clone_dir)
    if not os.path.isdir(clone_dir):
        print(f"Error: '{clone_dir}' is not a valid clone directory.")
        return

    print(f"""
╔══════════════════════════════════════════╗
║  🌐 WebClone Replay Server              ║
╠══════════════════════════════════════════╣
║  Serving: {clone_dir[:40]}...
║  URL:     http://localhost:{port}
║  API:     {len(os.listdir(os.path.join(clone_dir, 'data'))) if os.path.isdir(os.path.join(clone_dir, 'data')) else 0} endpoints replayed
║  Storage: {'restored' if os.path.isfile(os.path.join(clone_dir, 'browser-storage.json')) else 'not available'}
╚══════════════════════════════════════════╝
Press Ctrl+C to stop.
""")

    handler = lambda *args: ReplayHandler(*args, directory=clone_dir)
    with socketserver.TCPServer(("", port), handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")
