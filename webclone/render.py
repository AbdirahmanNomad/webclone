"""
Render the live page with Playwright and return final HTML + URL + runtime captures.

Enhancements:
- Fetch/XHR/GraphQL recording → saved as JSON files
- Service Worker + Cache API capture
- Framework route interception (Nuxt _payload, Next _next/data, etc.)
- DOM Mutation Observer → wait for SPA content to stabilize
- Infinite scroll detection → scroll until height stops growing
- HAR export for debugging
- Browser storage export (localStorage, sessionStorage)
- Iframe capture (same-origin)
"""

from __future__ import annotations

import asyncio
import json
import hashlib
import os
import re
from typing import List, Optional, Tuple, Dict
from urllib.parse import urlparse, urljoin

_STATIC_SUFFIXES: Tuple[str, ...] = (
    ".woff2", ".woff", ".ttf", ".otf", ".eot",
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".ico", ".avif",
    ".css", ".js", ".mjs", ".cjs", ".map",
)

# Framework-specific route patterns to capture
_FRAMEWORK_ROUTES = [
    # Nuxt
    r'/_payload\.json',
    r'/__NUXT__',
    r'/_nuxt/',
    # Next.js
    r'/_next/data/',
    r'/_next/static/',
    # Astro
    r'/astro-island',
    # SvelteKit
    r'/__data\.json',
    # Remix
    r'/_remix/',
    # Service Workers
    r'/sw\.js',
    r'/service-worker\.js',
    r'/workbox-',
    r'/manifest\.webmanifest',
    r'/manifest\.json',
    # Common API patterns
    r'/api/',
    r'/graphql',
]


def _path_looks_static(url: str) -> bool:
    path = urlparse(url).path.lower()
    return any(path.endswith(s) for s in _STATIC_SUFFIXES)


def _should_record_response(url: str, content_type: str) -> bool:
    if not url.startswith(("http://", "https://")):
        return False
    if url.startswith("data:") or url.startswith("blob:"):
        return False
    ct = (content_type or "").split(";")[0].strip().lower()
    if ct.startswith(("image/", "font/", "video/", "audio/")):
        return True
    if ct in ("text/css",):
        return True
    if "javascript" in ct or "ecmascript" in ct:
        return True
    if "json" in ct and ("application/" in ct or "text/" in ct):
        return True
    if "font" in ct and ("woff" in ct or "ttf" in ct or "opentype" in ct or "sfnt" in ct):
        return True
    if ct in ("application/octet-stream", "binary/octet-stream") and _path_looks_static(url):
        return True
    return _path_looks_static(url)


def _is_framework_route(url: str) -> bool:
    """Check if URL matches known framework patterns."""
    return any(re.search(p, url) for p in _FRAMEWORK_ROUTES)


_DARK_INIT_SCRIPT = """
(() => {
  try {
    const r = document.documentElement;
    r.classList.add('dark');
    r.setAttribute('data-theme', 'dark');
    r.style.colorScheme = 'dark';
  } catch (e) {}
})();
"""

_FETCH_RECORDING_SCRIPT = """
(() => {
  // Intercept fetch() calls
  const _origFetch = window.fetch;
  window.__webclone_fetch_log = [];
  window.fetch = async function(...args) {
    const start = Date.now();
    try {
      const resp = await _origFetch.apply(this, args);
      const clone = resp.clone();
      try {
        const text = await clone.text();
        window.__webclone_fetch_log.push({
          url: typeof args[0] === 'string' ? args[0] : args[0].url,
          method: args[1]?.method || 'GET',
          status: resp.status,
          type: resp.headers.get('content-type') || '',
          body: text.substring(0, 50000),
          duration: Date.now() - start
        });
      } catch(e) {}
      return resp;
    } catch(e) {
      window.__webclone_fetch_log.push({
        url: typeof args[0] === 'string' ? args[0] : args[0].url,
        method: args[1]?.method || 'GET',
        status: 0,
        type: 'error',
        body: '',
        error: e.message,
        duration: Date.now() - start
      });
      throw e;
    }
  };

  // Intercept XHR
  const _origOpen = XMLHttpRequest.prototype.open;
  const _origSend = XMLHttpRequest.prototype.send;
  XMLHttpRequest.prototype.open = function(method, url) {
    this.__webclone_method = method;
    this.__webclone_url = url;
    this.__webclone_start = Date.now();
    return _origOpen.apply(this, arguments);
  };
  XMLHttpRequest.prototype.send = function(body) {
    this.addEventListener('loadend', function() {
      window.__webclone_fetch_log.push({
        url: this.__webclone_url,
        method: this.__webclone_method,
        status: this.status,
        type: this.getResponseHeader('content-type') || '',
        body: this.responseText?.substring(0, 50000) || '',
        duration: Date.now() - this.__webclone_start
      });
    });
    return _origSend.apply(this, arguments);
  };
})();
"""

_MUTATION_OBSERVER_SCRIPT = """
(() => {
  window.__webclone_dom_stable = false;
  window.__webclone_mutation_count = 0;
  window.__webclone_last_mutation = Date.now();

  const observer = new MutationObserver((mutations) => {
    window.__webclone_mutation_count += mutations.length;
    window.__webclone_last_mutation = Date.now();
  });

  observer.observe(document.documentElement || document.body, {
    childList: true,
    subtree: true,
    attributes: true,
    characterData: true,
  });
})();
"""

_BROWSER_STORAGE_SCRIPT = """
(() => {
  window.__webclone_storage = {};
  try {
    window.__webclone_storage.localStorage = {};
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      window.__webclone_storage.localStorage[key] = localStorage.getItem(key);
    }
  } catch(e) {}
  try {
    window.__webclone_storage.sessionStorage = {};
    for (let i = 0; i < sessionStorage.length; i++) {
      const key = sessionStorage.key(i);
      window.__webclone_storage.sessionStorage[key] = sessionStorage.getItem(key);
    }
  } catch(e) {}
  try {
    window.__webclone_storage.cookies = document.cookie;
  } catch(e) {}
})();
"""

_SERVICE_WORKER_SCRIPT = """
(() => {
  window.__webclone_sw_registrations = [];
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.getRegistrations().then(regs => {
      regs.forEach(r => {
        window.__webclone_sw_registrations.push({
          scope: r.scope,
          active: r.active ? r.active.scriptURL : null,
          waiting: r.waiting ? r.waiting.scriptURL : null,
        });
      });
    });
  }
})();
"""


async def _wait_for_dom_stable(page, max_wait_ms=15000, quiet_ms=2000):
    """Wait for DOM mutations to settle (SPA content loaded)."""
    await page.evaluate(_MUTATION_OBSERVER_SCRIPT)

    start = asyncio.get_event_loop().time() * 1000
    while True:
        await asyncio.sleep(0.5)
        elapsed = asyncio.get_event_loop().time() * 1000 - start
        last_mut = await page.evaluate("window.__webclone_last_mutation")
        time_since = asyncio.get_event_loop().time() * 1000 - last_mut

        if time_since >= quiet_ms:
            break
        if elapsed >= max_wait_ms:
            break


async def _infinite_scroll_detect(page, max_scrolls=20, settle_ms=1500):
    """Scroll down until page height stops growing."""
    prev_height = await page.evaluate("document.body.scrollHeight")
    scrolls = 0

    while scrolls < max_scrolls:
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(1.0)
        new_height = await page.evaluate("document.body.scrollHeight")

        if new_height == prev_height:
            await asyncio.sleep(settle_ms / 1000)
            new_height = await page.evaluate("document.body.scrollHeight")
            if new_height == prev_height:
                break

        prev_height = new_height
        scrolls += 1

    # Scroll back to top
    await page.evaluate("window.scrollTo(0, 0)")


async def _fetch_rendered_async(
    url: str,
    *,
    timeout_ms: int = 60_000,
    settle_s: float = 3.0,
    dual_theme_pass: bool = True,
    record_fetch: bool = True,
    record_sw: bool = True,
    scroll_detect: bool = True,
    wait_for_spa: bool = True,
    capture_storage: bool = True,
    capture_iframes: bool = True,
    har_export: bool = True,
    output_dir: str = ".",
) -> dict:
    """
    Rendered page capture with full runtime recording.

    Returns dict with keys:
      - html: final DOM HTML
      - final_url: URL after redirects
      - network_hints: [(url, content_type), ...]
      - fetch_log: [{url, method, status, type, body, duration}, ...]
      - framework_routes: [url, ...]
      - sw_registrations: [{scope, active, waiting}, ...]
      - browser_storage: {localStorage, sessionStorage, cookies}
      - har: HAR log dict (if har_export=True)
    """
    from playwright.async_api import async_playwright

    result: Dict = {
        "html": None,
        "final_url": None,
        "network_hints": [],
        "fetch_log": [],
        "framework_routes": [],
        "sw_registrations": [],
        "browser_storage": {},
        "har": None,
    }

    merged_hints: List[Tuple[str, str]] = []
    seen_urls: set = set()
    fetch_responses: List[dict] = []
    fw_routes: List[str] = []

    async def _capture_json_response(response, url, ct):
        try:
            body = await response.text()
            fetch_responses.append({
                "url": url,
                "status": response.status,
                "type": ct,
                "body": body[:100000] if body else "",
            })
        except Exception:
            pass

    def on_response(response) -> None:
        try:
            u = response.url
            if u in seen_urls:
                return
            ct = response.headers.get("content-type", "") or ""

            # Record fetch/XHR JSON responses
            if "json" in ct and "application/" in ct:
                seen_urls.add(u)
                asyncio.ensure_future(_capture_json_response(response, u, ct))

            # Record framework routes
            if _is_framework_route(u):
                fw_routes.append(u)

            # Standard asset recording
            if not _should_record_response(u, ct):
                return
            seen_urls.add(u)
            merged_hints.append((u, ct))
        except Exception:
            pass

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        html_out: Optional[str] = None
        final_out: Optional[str] = None

        try:
            passes: List[Tuple[str, bool]] = [("light", False), ("dark", True)]
            if not dual_theme_pass:
                passes = [("dark", True)]

            for color_scheme, use_dark_script in passes:
                har_path = os.path.join(output_dir, "network.har") if har_export and use_dark_script else None
                context = await browser.new_context(
                    color_scheme=color_scheme,
                    record_har_path=har_path,
                )
                if use_dark_script:
                    await context.add_init_script(_DARK_INIT_SCRIPT)
                if record_fetch:
                    await context.add_init_script(_FETCH_RECORDING_SCRIPT)
                if wait_for_spa:
                    await context.add_init_script(_MUTATION_OBSERVER_SCRIPT)
                if capture_storage:
                    await context.add_init_script(_BROWSER_STORAGE_SCRIPT)
                if record_sw:
                    await context.add_init_script(_SERVICE_WORKER_SCRIPT)

                page = await context.new_page()
                page.on("response", on_response)

                await page.goto(url, timeout=timeout_ms, wait_until="domcontentloaded")

                try:
                    await page.wait_for_load_state(
                        "networkidle", timeout=min(30_000, timeout_ms)
                    )
                except Exception:
                    pass

                # Wait for SPA to stabilize
                if wait_for_spa and use_dark_script:
                    try:
                        await _wait_for_dom_stable(page)
                    except Exception:
                        pass

                # Infinite scroll detection
                if scroll_detect and use_dark_script:
                    try:
                        await _infinite_scroll_detect(page)
                    except Exception:
                        pass

                if settle_s > 0:
                    await asyncio.sleep(settle_s)

                if use_dark_script or not dual_theme_pass:
                    html_out = await page.content()
                    final_out = page.url

                    # Collect fetch log
                    if record_fetch:
                        try:
                            flog = await page.evaluate("window.__webclone_fetch_log")
                            if flog:
                                result["fetch_log"] = flog
                        except Exception:
                            pass

                    # Collect browser storage
                    if capture_storage:
                        try:
                            storage = await page.evaluate("window.__webclone_storage")
                            if storage:
                                result["browser_storage"] = storage
                        except Exception:
                            pass

                    # Collect SW registrations
                    if record_sw:
                        try:
                            sw = await page.evaluate("window.__webclone_sw_registrations")
                            if sw:
                                result["sw_registrations"] = sw
                        except Exception:
                            pass

                    # Capture same-origin iframes
                    if capture_iframes:
                        try:
                            frames = page.frames
                            for frame in frames:
                                if frame != page.main_frame:
                                    try:
                                        frame_url = frame.url
                                        frame_html = await frame.content()
                                        result.setdefault("iframes", []).append({
                                            "url": frame_url,
                                            "html": frame_html[:500000],
                                        })
                                    except Exception:
                                        pass
                        except Exception:
                            pass

                    # HAR export
                    if har_export:
                        try:
                            read_har_path = os.path.join(output_dir, "network.har")
                            if os.path.exists(read_har_path):
                                with open(read_har_path, "r") as f:
                                    result["har"] = json.load(f)
                        except Exception:
                            pass

                await context.close()

            result["html"] = html_out
            result["final_url"] = final_out or url
            result["network_hints"] = merged_hints
            result["framework_routes"] = list(set(fw_routes))
            result["fetch_log"].extend(fetch_responses)

            return result

        finally:
            await browser.close()


def fetch_rendered_html(
    url: str,
    *,
    output_dir: str = ".",
    **kwargs,
) -> dict:
    """Sync entry point. Returns dict with full capture data."""
    return asyncio.run(_fetch_rendered_async(url, output_dir=output_dir, **kwargs))
