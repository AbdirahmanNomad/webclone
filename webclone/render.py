"""
Render the live page with Playwright and return final HTML + URL.
Collects response URLs (fonts, images, CSS, JS) so the cloner can fetch
assets that never appear as static tags in the DOM.

Uses dark color scheme + optional light pass so:
- prefers-color-scheme: dark CSS and assets load
- light-only assets still appear in the merged network hint list
"""

from __future__ import annotations

import asyncio
from typing import List, Optional, Tuple
from urllib.parse import urlparse

# Paths that often point at static bytes (even when Content-Type is wrong).
_STATIC_SUFFIXES: Tuple[str, ...] = (
    ".woff2",
    ".woff",
    ".ttf",
    ".otf",
    ".eot",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".svg",
    ".ico",
    ".avif",
    ".css",
    ".js",
    ".mjs",
    ".cjs",
    ".map",
)


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


async def _fetch_rendered_async(
    url: str,
    *,
    timeout_ms: int = 60_000,
    settle_s: float = 3.0,
    dual_theme_pass: bool = True,
) -> Tuple[Optional[str], Optional[str], List[Tuple[str, str]]]:
    from playwright.async_api import async_playwright

    merged_hints: List[Tuple[str, str]] = []
    seen_urls: set = set()

    def on_response(response) -> None:
        try:
            u = response.url
            if u in seen_urls:
                return
            ct = response.headers.get("content-type", "") or ""
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
                context = await browser.new_context(color_scheme=color_scheme)
                if use_dark_script:
                    await context.add_init_script(_DARK_INIT_SCRIPT)
                page = await context.new_page()
                page.on("response", on_response)
                await page.goto(url, timeout=timeout_ms, wait_until="domcontentloaded")
                try:
                    await page.wait_for_load_state(
                        "networkidle", timeout=min(30_000, timeout_ms)
                    )
                except Exception:
                    pass
                if settle_s > 0:
                    await asyncio.sleep(settle_s)
                if use_dark_script or not dual_theme_pass:
                    html_out = await page.content()
                    final_out = page.url
                await context.close()

            return html_out, final_out or url, merged_hints
        finally:
            await browser.close()


def fetch_rendered_html(
    url: str,
    *,
    timeout_ms: int = 60_000,
    settle_s: float = 3.0,
    dual_theme_pass: bool = True,
) -> Tuple[Optional[str], Optional[str], List[Tuple[str, str]]]:
    """Sync entry: rendered HTML (dark-themed), final URL, merged network hints."""
    return asyncio.run(
        _fetch_rendered_async(
            url,
            timeout_ms=timeout_ms,
            settle_s=settle_s,
            dual_theme_pass=dual_theme_pass,
        )
    )
