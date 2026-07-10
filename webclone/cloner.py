#!/usr/bin/env python3
"""
WebClone - Universal Website Cloner
Clone any website with its complete design, styles, scripts, and assets.

Author: Abdirahman Ahmed
GitHub: https://github.com/AbdirahmanNomad/webclone
Website: https://abdirahman.net
License: MIT

Usage:
    webclone <url> [output_directory]
    
Example:
    webclone https://example.com my_cloned_site
"""

import os
import sys
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urlunparse
import re
import json
from pathlib import Path
import hashlib
from datetime import datetime

# CSS url(...) — quoted or unquoted; skips are handled after extract.
_CSS_URL_RE = re.compile(
    r"""url\(\s*(?:(')([^']*)'|(")([^"]*)"|([^)]*?))\s*\)""",
    re.IGNORECASE,
)

_IMPORT_START_RE = re.compile(r"@import\b\s*", re.IGNORECASE)


def _parse_srcset_tokens(srcset: str):
    """Yield URL candidates from an HTML srcset value (handles descriptors like 1x / 320w)."""
    if not srcset or not srcset.strip():
        return
    for chunk in srcset.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        url = chunk.split()[0].strip()
        if url and not url.lower().startswith("data:"):
            yield url


def _link_rel_joined(link) -> str:
    rel = link.get("rel") or []
    if isinstance(rel, str):
        rel = [rel]
    return " ".join(str(x).lower() for x in rel)


def _is_stylesheet_href_link(link) -> bool:
    """True for stylesheet, alternate stylesheet, and preload-as-style links."""
    if not link.get("href"):
        return False
    rj = _link_rel_joined(link)
    if "stylesheet" in rj:
        return True
    if "preload" in rj and (link.get("as") or "").lower() == "style":
        return True
    return False


class UniversalWebsiteCloner:
    def __init__(self, url, output_dir=None):
        self.url = url
        self.base_url = self._get_base_url(url)
        
        # Generate output directory name from URL if not provided
        if output_dir is None:
            parsed = urlparse(url)
            domain = parsed.netloc.replace('www.', '').replace('.', '_')
            output_dir = f"{domain}_cloned"
        
        self.output_dir = output_dir
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        # Track downloaded files to avoid duplicates
        self.downloaded_files = {}
        self.failed_downloads = []
        self._used_local_paths = set()
        self._css_entries = []

    def _resource_type_from_network_hint(self, url: str, content_type: str) -> str:
        """Map a browser response to a download bucket (font, image, css, js, file)."""
        ct = (content_type or "").split(";")[0].strip().lower()
        path = (urlparse(url).path or "").lower()

        if ct.startswith("font/") or "font-woff" in ct or "x-font-" in ct or "opentype" in ct:
            return "font"
        if path.endswith((".woff2", ".woff", ".ttf", ".otf", ".eot")):
            return "font"
        if ct.startswith("image/"):
            return "image"
        if path.endswith(
            (".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".ico", ".avif")
        ):
            return "image"
        if ct == "text/css" or path.endswith(".css"):
            return "css"
        if "javascript" in ct or "ecmascript" in ct:
            return "js"
        if path.endswith((".js", ".mjs", ".cjs")):
            return "js"
        if ct.startswith(("video/", "audio/")):
            return "file"
        return "file"

    def _download_network_hints(self, hints, resources_downloaded):
        """Fetch assets the browser loaded but that may not appear in static HTML/CSS."""
        if not hints:
            return
        print("\n📦 Downloading assets seen in browser (fonts, lazy images, bundles)…")
        for url, ctype in hints:
            canon = self._canonicalize_url(url, base_url=None)
            if not canon or canon in self.downloaded_files:
                continue
            rtype = self._resource_type_from_network_hint(url, ctype)
            if not self.download_resource(url, rtype, base_url=None):
                continue
            if rtype == "font":
                resources_downloaded["fonts"] += 1
            elif rtype == "image":
                resources_downloaded["images"] += 1
            elif rtype == "css":
                resources_downloaded["css"] += 1
            elif rtype == "js":
                resources_downloaded["js"] += 1
            else:
                resources_downloaded["other"] += 1

    def _substitute_known_remote_urls(self, text: str) -> str:
        """Replace any absolute URL we saved with its local path (offline @font-face, srcset, etc.)."""
        if not text or not self.downloaded_files:
            return text
        for remote in sorted(self.downloaded_files.keys(), key=len, reverse=True):
            local = self.downloaded_files[remote]
            if remote in text:
                text = text.replace(remote, local)
        return text

    def _substitute_urls_in_saved_assets(self):
        """Second pass: point remaining remote URLs to downloaded files in CSS + HTML."""
        root = Path(self.output_dir)
        paths = list(root.rglob("*.css"))
        idx = root / "index.html"
        if idx.is_file():
            paths.append(idx)
        for path in paths:
            try:
                t = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            nt = self._substitute_known_remote_urls(t)
            if nt != t:
                try:
                    path.write_text(nt, encoding="utf-8", newline="")
                except OSError:
                    pass

    def _get_base_url(self, url):
        """Get base URL for the site"""
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"

    def _canonicalize_url(self, maybe_relative_url, base_url=None):
        """
        Convert a possibly-relative URL into a canonical absolute URL for caching/lookup.
        Keeps querystring (often used for cache-busting), drops fragments.
        base_url: resolve relatives against this (e.g. the CSS file URL). Defaults to site origin.
        """
        if not maybe_relative_url:
            return None

        raw = maybe_relative_url.strip()
        # Skip data URLs and non-http(s) early
        if raw.startswith("data:"):
            return None
        if raw.startswith("#"):
            return None

        base = self.base_url if base_url is None else base_url
        absolute = urljoin(base, raw)
        parsed = urlparse(absolute)

        if parsed.scheme not in ("http", "https"):
            return None

        # Normalize host/scheme casing, remove fragment
        netloc = parsed.netloc.lower()
        scheme = parsed.scheme.lower()

        # Remove default ports
        if (scheme == "http" and netloc.endswith(":80")) or (scheme == "https" and netloc.endswith(":443")):
            netloc = netloc.rsplit(":", 1)[0]

        # Normalize empty path
        path = parsed.path or "/"

        return urlunparse((scheme, netloc, path, parsed.params, parsed.query, ""))

    def _resource_type_for_css_ref(self, canonical_url):
        """Guess asset kind for a URL referenced from CSS (fonts, images, nested CSS)."""
        p = (urlparse(canonical_url).path or "").lower()
        if p.endswith((".woff2", ".woff", ".ttf", ".otf", ".eot")):
            return "font"
        if p.endswith((".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".avif", ".ico")):
            return "image"
        if p.endswith(".css"):
            return "css"
        return "image"

    def _relpath_for_css(self, css_local_path, asset_local_path):
        """POSIX relpath from the CSS file to the saved asset, for url(...) in CSS."""
        css_dir = os.path.join(self.output_dir, os.path.dirname(css_local_path))
        asset_abs = os.path.join(self.output_dir, asset_local_path)
        rel = os.path.relpath(asset_abs, css_dir)
        return rel.replace(os.sep, "/")

    def _import_href_and_media(self, body):
        """Parse @import prelude (after @import keyword): href and optional media query tail."""
        s = body.strip()
        if not s:
            return None, ""
        low = s.lower()
        if low.startswith("url("):
            depth = 0
            for i, ch in enumerate(s):
                if ch == "(":
                    depth += 1
                elif ch == ")":
                    depth -= 1
                    if depth == 0:
                        inner = s[4:i].strip()
                        if len(inner) >= 2 and inner[0] == inner[-1] and inner[0] in "'\"":
                            inner = inner[1:-1]
                        href = inner.strip()
                        media = s[i + 1 :].strip()
                        return href, media
            return None, ""
        if s[0] in "'\"":
            q = s[0]
            j = s.find(q, 1)
            if j != -1:
                return s[1:j].strip(), s[j + 1 :].strip()
        return None, ""

    def _rewrite_css_text(self, css_text, css_canonical, css_local_path, resources_downloaded):
        """Download url(...) / @import targets, rewrite CSS to local relative paths."""
        queue_css = []

        # @import first so url() inside import lines is not rewritten before we parse imports.
        css_text, more_from_imports = self._rewrite_css_imports(
            css_text, css_canonical, css_local_path, resources_downloaded
        )
        queue_css.extend(more_from_imports)

        segments = []
        last = 0
        for m in _CSS_URL_RE.finditer(css_text):
            # Groups: (' quote) (single-quoted) (' double) (double-quoted) OR (unquoted)
            if m.group(1) is not None:
                inner = m.group(2) or ""
                quote = "'"
            elif m.group(3) is not None:
                inner = m.group(4) or ""
                quote = '"'
            else:
                inner = (m.group(5) or "").strip()
                quote = ""

            inner = inner.strip()
            segments.append(css_text[last:m.start()])
            last = m.end()

            if not inner or inner.startswith("data:") or inner.startswith("#"):
                segments.append(m.group(0))
                continue

            canonical = self._canonicalize_url(inner, base_url=css_canonical)
            if not canonical:
                segments.append(m.group(0))
                continue

            rtype = self._resource_type_for_css_ref(canonical)
            local = self.download_resource(inner, rtype, base_url=css_canonical)
            if not local:
                segments.append(m.group(0))
                continue

            if rtype == "css":
                resources_downloaded["css"] += 1
                queue_css.append((canonical, local))
            elif rtype == "font":
                resources_downloaded["fonts"] += 1
            elif rtype == "image":
                resources_downloaded["images"] += 1
            else:
                resources_downloaded["other"] += 1

            rel = self._relpath_for_css(css_local_path, local)
            segments.append(f"url({quote}{rel}{quote})")

        segments.append(css_text[last:])
        new_text = "".join(segments)
        return new_text, queue_css

    def _rewrite_css_imports(self, css_text, css_canonical, css_local_path, resources_downloaded):
        """Rewrite @import rules to local CSS paths; return (text, new_css_entries)."""
        parts = []
        last = 0
        extra_entries = []

        for m in _IMPORT_START_RE.finditer(css_text):
            start = m.start()
            semi = css_text.find(";", m.end())
            if semi == -1:
                continue

            body = css_text[m.end():semi]
            href, media_tail = self._import_href_and_media(body)
            if not href or href.startswith("data:"):
                continue

            canonical = self._canonicalize_url(href, base_url=css_canonical)
            if not canonical:
                continue

            local = self.download_resource(href, "css", base_url=css_canonical)
            if not local:
                continue

            resources_downloaded["css"] += 1
            extra_entries.append((canonical, local))
            rel = self._relpath_for_css(css_local_path, local)

            parts.append(css_text[last:start])
            if media_tail:
                parts.append(f'@import url("{rel}") {media_tail};')
            else:
                parts.append(f'@import url("{rel}");')
            last = semi + 1

        parts.append(css_text[last:])
        return "".join(parts), extra_entries

    def _process_downloaded_css(self, resources_downloaded):
        """Follow url(...) and @import inside saved stylesheets; rewrite files on disk."""
        queue = list(self._css_entries)
        seen_paths = set()

        print("\n📦 Processing CSS (fonts, images, @import)...")

        while queue:
            css_canonical, css_local_path = queue.pop(0)
            if css_local_path in seen_paths:
                continue
            seen_paths.add(css_local_path)

            full_css = os.path.join(self.output_dir, css_local_path)
            if not os.path.isfile(full_css):
                continue

            try:
                with open(full_css, "r", encoding="utf-8", errors="replace") as f:
                    original = f.read()
            except OSError:
                continue

            new_text, new_queue = self._rewrite_css_text(
                original, css_canonical, css_local_path, resources_downloaded
            )
            for item in new_queue:
                if item not in queue and item[1] not in seen_paths:
                    queue.append(item)

            if new_text != original:
                with open(full_css, "w", encoding="utf-8", newline="") as f:
                    f.write(new_text)
    
    def _is_internal_link(self, url):
        """Check if a URL belongs to the same site."""
        parsed = urlparse(url)
        base = urlparse(self.base_url)
        if not parsed.netloc:
            return True  # relative link
        return parsed.netloc == base.netloc

    def _discover_pages(self, soup, current_url):
        """Find all internal page links (HTML pages, not assets)."""
        pages = set()
        asset_exts = ('.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg',
                      '.ico', '.avif', '.woff', '.woff2', '.ttf', '.eot', '.otf',
                      '.mp4', '.mp3', '.pdf', '.json', '.xml', '.txt', '.map')

        for a in soup.find_all('a', href=True):
            href = a['href'].strip()
            if not href or href.startswith(('#', 'javascript:', 'mailto:', 'tel:', 'data:')):
                continue

            # Skip asset files
            if any(href.lower().endswith(ext) for ext in asset_exts):
                continue

            canonical = self._canonicalize_url(href)
            if not canonical or not self._is_internal_link(canonical):
                continue

            # Normalize: strip query/fragment for dedup
            parsed = urlparse(canonical)
            clean = urlunparse((parsed.scheme, parsed.netloc, parsed.path, '', '', ''))
            pages.add(clean)

        return pages

    def _save_page(self, html, url, filename):
        """Save an HTML page with resource path updates."""
        soup = BeautifulSoup(html, 'html.parser')
        self.extract_and_download_resources(soup)
        soup = self.update_resource_paths(soup)

        path = os.path.join(self.output_dir, filename)
        os.makedirs(os.path.dirname(path) if os.path.dirname(path) else '.', exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(str(soup))
        return path

    def _crawl_pages(self, start_url, max_pages=50):
        """Recursively crawl and download all internal pages."""
        visited = set()
        queue = [start_url]
        page_count = 0

        print(f"\n🕷️  Crawling pages (max {max_pages})...")

        while queue and page_count < max_pages:
            url = queue.pop(0)
            if url in visited:
                continue
            visited.add(url)

            try:
                resp = self.session.get(url, timeout=20)
                if resp.status_code != 200:
                    continue
                if 'text/html' not in (resp.headers.get('content-type', '') or ''):
                    continue
            except Exception:
                continue

            soup = BeautifulSoup(resp.text, 'html.parser')

            # Determine output filename
            parsed = urlparse(url)
            path = parsed.path.lstrip('/')
            if not path or path.endswith('/'):
                filename = os.path.join(path, 'index.html') if path else 'index.html'
            elif '.' not in path.split('/')[-1]:
                filename = path + '.html'
            else:
                filename = path

            # Handle query strings in filename
            if parsed.query:
                qs = parsed.query.replace('=', '-').replace('&', '-')[:50]
                base, ext = os.path.splitext(filename)
                filename = f"{base}?{qs}{ext or '.html'}"

            print(f"  📄 {filename}")
            self._save_page(resp.text, url, filename)
            page_count += 1

            # Discover more pages
            new_pages = self._discover_pages(soup, url)
            for p in new_pages:
                if p not in visited and p not in queue:
                    queue.append(p)

        print(f"  ✓ Crawled {page_count} pages")
        return page_count

    def _discover_module_chunks(self, soup):
        """Find all modulepreload links to ensure all JS chunks are downloaded."""
        chunks = []
        for link in soup.find_all('link', rel='modulepreload'):
            href = link.get('href')
            if href:
                chunks.append(href)
        # Also check script[type=module] for dynamic imports
        for script in soup.find_all('script', type='module'):
            src = script.get('src')
            if src:
                chunks.append(src)
        return chunks

    def create_directory_structure(self):
        """Create the output directory structure"""
        directories = [
            self.output_dir,
            f"{self.output_dir}/assets",
            f"{self.output_dir}/assets/css",
            f"{self.output_dir}/assets/js",
            f"{self.output_dir}/assets/images",
            f"{self.output_dir}/assets/fonts",
            f"{self.output_dir}/assets/files",
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory structure in '{self.output_dir}'")
    
    def fetch_page(self, url=None):
        """Fetch HTML: Playwright (rendered DOM) first, then HTTP fallback."""
        if url is None:
            url = self.url

        try:
            from .render import fetch_rendered_html

            print(
                f"Rendering {url} in browser (Playwright, light+dark theme pass)…"
            )
            html, final_url, hints = fetch_rendered_html(url)
            if html:
                print("✓ Got rendered page (dark preference + dark DOM hooks)")
                if hints:
                    print(f"   ({len(hints)} network responses recorded for asset download)")
                return html, final_url or url, hints
        except ImportError:
            print(
                "ℹ️  Playwright not installed — using plain HTTP fetch.\n"
                "   For JS-rendered sites: pip install playwright && playwright install chromium"
            )
        except Exception as e:
            print(f"✗ Browser render failed ({e}); trying HTTP…")

        try:
            print(f"Fetching {url} (HTTP)…")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            print("✓ Successfully fetched page")
            return response.text, response.url, []
        except Exception as e:
            print(f"✗ Error fetching page: {e}")
            return None, None, []
    
    def _get_file_extension(self, url, content_type=None):
        """Determine file extension from URL or content type"""
        parsed = urlparse(url)
        path = parsed.path
        
        # Try to get extension from URL
        if '.' in path.split('/')[-1]:
            return path.split('.')[-1].lower()
        
        # Fallback to content type
        if content_type:
            ct = content_type.split(";")[0].strip().lower()
            extensions = {
                "text/css": "css",
                "text/javascript": "js",
                "application/javascript": "js",
                "application/json": "json",
                "image/jpeg": "jpg",
                "image/png": "png",
                "image/gif": "gif",
                "image/svg+xml": "svg",
                "image/webp": "webp",
                "font/woff": "woff",
                "font/woff2": "woff2",
                "application/font-woff": "woff",
                "application/font-woff2": "woff2",
                "application/x-font-woff": "woff",
                "application/x-font-ttf": "ttf",
                "font/ttf": "ttf",
                "font/otf": "otf",
                "application/vnd.ms-fontobject": "eot",
            }
            return extensions.get(ct, "bin")
        
        return 'bin'
    
    def _get_local_path(self, canonical_url, resource_type="file", content_type=None):
        """Generate a collision-resistant local path for a resource."""
        parsed = urlparse(canonical_url)
        remote_path = (parsed.path or "/").lstrip("/")

        # Handle empty paths / directory paths
        if not remote_path or remote_path.endswith("/"):
            remote_path = remote_path + "index.html"

        ext = self._get_file_extension(canonical_url, content_type)
        url_hash = hashlib.md5(canonical_url.encode("utf-8")).hexdigest()[:10]

        # Create subdirectory based on resource type
        type_dirs = {
            'css': 'assets/css',
            'js': 'assets/js',
            'image': 'assets/images',
            'font': 'assets/fonts',
            'file': 'assets/files',
        }
        
        # Preserve build asset paths EXACTLY (no hashing) for frameworks: Nuxt, Next.js, etc.
        # This keeps modulepreload/dynamic-import paths working.
        if remote_path.startswith(("_nuxt/", "_next/", "assets/", "static/", "cms/", "css/", "fonts/", "js/", "images/")):
            candidate = remote_path
        else:
            stem = os.path.splitext(os.path.basename(remote_path))[0] or "file"
            filename = f"{stem}-{url_hash}.{ext}"
            candidate = f"{type_dirs.get(resource_type, type_dirs['file'])}/{filename}"

        # Ensure uniqueness within this run (extra safety)
        if candidate in self._used_local_paths:
            candidate = f"{type_dirs.get(resource_type, type_dirs['file'])}/{stem}-{url_hash}-{hashlib.md5((canonical_url + candidate).encode('utf-8')).hexdigest()[:6]}.{ext}"

        self._used_local_paths.add(candidate)
        return candidate
    
    def download_resource(self, url, resource_type="file", base_url=None):
        """Download a resource (CSS, JS, image, etc.)"""
        canonical_url = self._canonicalize_url(url, base_url=base_url)
        if not canonical_url:
            return None

        # Skip if already downloaded
        if canonical_url in self.downloaded_files:
            return self.downloaded_files[canonical_url]
        
        # Skip if previously failed
        if canonical_url in self.failed_downloads:
            return None
            
        try:
            response = self.session.get(canonical_url, timeout=25, stream=True)
            response.raise_for_status()

            # Determine local path
            raw_ct = response.headers.get("content-type", "") or ""
            content_type = raw_ct.split(";")[0].strip().lower()
            local_path = self._get_local_path(
                canonical_url, resource_type, content_type=content_type
            )
            full_local_path = os.path.join(self.output_dir, local_path)
            
            # Create subdirectories as needed
            os.makedirs(os.path.dirname(full_local_path), exist_ok=True)
            
            # Determine if binary or text
            is_binary = any(
                t in content_type
                for t in ("image/", "font/", "octet-stream", "pdf", "video/", "audio/")
            ) or resource_type in ("font", "image")
            
            # Save the file
            mode = 'wb' if is_binary else 'w'
            with open(full_local_path, mode) as f:
                if is_binary:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                else:
                    f.write(response.text)
            
            # Cache the local path
            self.downloaded_files[canonical_url] = local_path
            
            print(f"  ✓ {resource_type}: {os.path.basename(local_path)}")
            if resource_type == "css":
                self._css_entries.append((canonical_url, local_path))
            return local_path
            
        except Exception as e:
            print(f"  ✗ Failed {url}: {str(e)[:50]}")
            self.failed_downloads.append(canonical_url)
            return None
    
    def extract_and_download_resources(self, soup):
        """Extract and download all resources from HTML"""
        self._css_entries = []
        resources_downloaded = {
            'css': 0,
            'js': 0,
            'images': 0,
            'fonts': 0,
            'other': 0
        }
        
        print("\n📦 Downloading CSS files...")
        _css_hrefs_done = set()
        for link in soup.find_all("link", href=True):
            if not _is_stylesheet_href_link(link):
                continue
            href = link["href"]
            if href in _css_hrefs_done:
                continue
            _css_hrefs_done.add(href)
            if self.download_resource(href, "css"):
                resources_downloaded["css"] += 1

        # Preload as image / font (covers hero / icon URLs)
        for link in soup.find_all("link", rel="preload"):
            as_attr = (link.get("as") or "").lower()
            href = link.get("href")
            if not href:
                continue
            if as_attr == "image":
                if self.download_resource(href, "image"):
                    resources_downloaded["images"] += 1
            elif as_attr == "font":
                if self.download_resource(href, "font"):
                    resources_downloaded["fonts"] += 1
        
        print("\n📦 Downloading JavaScript files...")
        # JavaScript files
        for script in soup.find_all('script', src=True):
            if script.get('src'):
                if self.download_resource(script['src'], 'js'):
                    resources_downloaded['js'] += 1
        
        # Preload scripts
        for link in soup.find_all('link', rel='preload', as_='script'):
            if link.get('href'):
                if self.download_resource(link['href'], 'js'):
                    resources_downloaded['js'] += 1
        
        print("\n📦 Downloading images...")
        # Images with src
        for img in soup.find_all('img', src=True):
            if img.get('src'):
                if self.download_resource(img['src'], 'image'):
                    resources_downloaded['images'] += 1

        # Lazy / responsive images
        for img in soup.find_all("img", attrs={"data-src": True}):
            if self.download_resource(img["data-src"], "image"):
                resources_downloaded["images"] += 1
        for img in soup.find_all("img", attrs={"data-srcset": True}):
            for u in _parse_srcset_tokens(img.get("data-srcset", "")):
                if self.download_resource(u, "image"):
                    resources_downloaded["images"] += 1
        
        # Images with srcset (relative URLs, protocol-relative, descriptors)
        for img in soup.find_all('img', srcset=True):
            for u in _parse_srcset_tokens(img.get('srcset', '')):
                if self.download_resource(u, 'image'):
                    resources_downloaded['images'] += 1

        for source in soup.find_all("source", src=True):
            if source.get("src"):
                if self.download_resource(source["src"], "image"):
                    resources_downloaded["images"] += 1
        for source in soup.find_all("source", srcset=True):
            for u in _parse_srcset_tokens(source.get("srcset", "")):
                if self.download_resource(u, "image"):
                    resources_downloaded["images"] += 1

        for video in soup.find_all("video", poster=True):
            if video.get("poster"):
                if self.download_resource(video["poster"], "image"):
                    resources_downloaded["images"] += 1
        
        # Background images in style attributes
        for elem in soup.find_all(style=True):
            style = elem['style']
            urls = re.findall(r'url\([\'"]?([^\'"]+)[\'"]?\)', style)
            for url in urls:
                if self.download_resource(url, 'image'):
                    resources_downloaded['images'] += 1

        # Inline <style> blocks (fonts / backgrounds not in external CSS yet)
        for style_tag in soup.find_all("style"):
            block = style_tag.string or style_tag.get_text() or ""
            for m in _CSS_URL_RE.finditer(block):
                if m.group(1) is not None:
                    inner = (m.group(2) or "").strip()
                elif m.group(3) is not None:
                    inner = (m.group(4) or "").strip()
                else:
                    inner = (m.group(5) or "").strip()
                if not inner or inner.startswith("data:") or inner.startswith("#"):
                    continue
                canon = self._canonicalize_url(inner)
                if not canon:
                    continue
                rtype = self._resource_type_for_css_ref(canon)
                if self.download_resource(inner, rtype):
                    if rtype == "font":
                        resources_downloaded["fonts"] += 1
                    elif rtype == "css":
                        resources_downloaded["css"] += 1
                    elif rtype == "image":
                        resources_downloaded["images"] += 1
                    else:
                        resources_downloaded["other"] += 1

        # Favicons / app icons
        for link in soup.find_all("link", href=True):
            rel = link.get("rel")
            rel_vals = rel if isinstance(rel, list) else ([rel] if rel else [])
            joined = " ".join(str(x) for x in rel_vals).lower()
            if not any(
                k in joined
                for k in ("icon", "apple-touch", "mask-icon", "shortcut")
            ):
                continue
            if self.download_resource(link["href"], "image"):
                resources_downloaded["images"] += 1
        
        print("\n📦 Downloading fonts...")
        # Fonts (from preload links)
        for link in soup.find_all('link', rel='preload', as_='font'):
            if link.get('href'):
                if self.download_resource(link['href'], 'font'):
                    resources_downloaded['fonts'] += 1
        
        return resources_downloaded
    
    def update_resource_paths(self, soup):
        """Update resource paths in HTML to point to local files"""
        # Update stylesheets
        for link in soup.find_all('link', href=True):
            original_href = link['href']
            canonical = self._canonicalize_url(original_href)
            if canonical and canonical in self.downloaded_files:
                link['href'] = self.downloaded_files[canonical]
        
        # Update scripts
        for script in soup.find_all('script', src=True):
            original_src = script['src']
            canonical = self._canonicalize_url(original_src)
            if canonical and canonical in self.downloaded_files:
                script['src'] = self.downloaded_files[canonical]
        
        # Update images
        for img in soup.find_all('img', src=True):
            original_src = img['src']
            canonical = self._canonicalize_url(original_src)
            if canonical and canonical in self.downloaded_files:
                img['src'] = self.downloaded_files[canonical]
        
        return soup
    
    def add_critical_css(self, soup):
        """Add critical CSS for better standalone functionality"""
        critical_css = """
        <style id="critical-css">
            /* Critical CSS for standalone functionality */
            * { box-sizing: border-box; }
            html { scroll-behavior: smooth; }
            body { margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif; }
            img { max-width: 100%; height: auto; }
            a { text-decoration: none; color: inherit; }
            button { cursor: pointer; }
        </style>
        """
        
        head = soup.find('head')
        if head:
            head.insert(0, BeautifulSoup(critical_css, 'html.parser'))
        
        return soup
    
    def save_html(self, html_content, final_url, network_hints=None, is_homepage=True):
        """Save the processed HTML file"""
        soup = BeautifulSoup(html_content, 'html.parser')

        # Download all resources
        resources = self.extract_and_download_resources(soup)
        self._download_network_hints(network_hints or [], resources)
        self._process_downloaded_css(resources)

        # Discover and download module chunks (dynamic imports)
        chunks = self._discover_module_chunks(soup)
        for chunk in chunks:
            rtype = 'js' if chunk.endswith('.js') else 'css' if chunk.endswith('.css') else 'file'
            self.download_resource(chunk, rtype)

        # Update paths to local files
        soup = self.update_resource_paths(soup)

        # Only add critical CSS + meta to homepage
        if is_homepage:
            soup = self.add_critical_css(soup)
            meta = soup.new_tag('meta', attrs={'name': 'cloned-from', 'content': self.url})
            if soup.head:
                soup.head.append(meta)

        # Save to index.html
        output_path = os.path.join(self.output_dir, 'index.html')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(str(soup.prettify()))

        self._substitute_urls_in_saved_assets()

        print(f"\n✓ Saved HTML to: {output_path}")
        return resources
    
    def create_readme(self, resources):
        """Create a README with clone information"""
        readme_content = f"""# Cloned Website

## Source
- **Original URL**: {self.url}
- **Cloned on**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Resources Downloaded
- 📄 CSS Files: {resources['css']}
- 📜 JavaScript Files: {resources['js']}
- 🖼️ Images: {resources['images']}
- 🔤 Fonts: {resources['fonts']}
- 📦 Other: {resources['other']}

## Directory Structure
```
{self.output_dir}/
├── index.html              # Main HTML file
└── assets/
    ├── css/               # Stylesheets
    ├── js/                # JavaScript files
    ├── images/            # Images
    ├── fonts/             # Web fonts
    └── files/             # Other assets
```

## How to Use

### Method 1: Direct Open
Simply open `index.html` in any modern web browser:
```bash
open index.html
```

### Method 2: Local Server (Recommended)
For full functionality, serve through a local web server:
```bash
cd {self.output_dir}
python -m http.server 8000
```
Then visit: http://localhost:8000

### Method 3: Live Server (VS Code)
If using VS Code, install the "Live Server" extension and right-click on `index.html` > "Open with Live Server"

## Notes
- Some dynamic features may require the original server
- External API calls will still go to the original domain
- Some resources may not work offline if they depend on external services
- This is a static clone - no backend functionality is included

## Reuse This Clone
This cloned website can be used as a template for your future projects:
1. Modify the HTML content in `index.html`
2. Customize styles in `assets/css/`
3. Add your own functionality in `assets/js/`
4. Replace images in `assets/images/`

---

**Cloned with [WebClone](https://github.com/AbdirahmanNomad/webclone)** by Abdirahman Ahmed  
⭐ Star us on GitHub | 📦 `pip install webclone-cli`
"""
        
        readme_path = os.path.join(self.output_dir, 'README.md')
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        print(f"✓ Created README: {readme_path}")
    
    def clone(self, crawl=True, max_pages=50):
        """Main cloning process"""
        print("=" * 70)
        print("🌐 WebClone - Universal Website Cloner")
        print("   By Abdirahman Ahmed | github.com/AbdirahmanNomad/webclone")
        print("=" * 70)
        print(f"Target URL: {self.url}")
        print(f"Output Dir: {self.output_dir}/")
        print(f"Crawl pages: {'Yes' if crawl else 'No'} (max {max_pages})")
        print("=" * 70)

        # Step 1: Create directory structure
        self.create_directory_structure()

        # Step 2: Fetch main HTML
        html_content, final_url, network_hints = self.fetch_page()
        if not html_content:
            print("\n✗ Failed to fetch page. Aborting.")
            return False

        # Update base URL if redirected
        if final_url and final_url != self.url:
            self.base_url = self._get_base_url(final_url)
            print(f"ℹ️  Redirected to: {final_url}")

        # Step 3: Download resources and save homepage
        resources = self.save_html(html_content, final_url, network_hints, is_homepage=True)

        # Step 4: Recursively crawl all internal pages
        if crawl:
            soup = BeautifulSoup(html_content, 'html.parser')
            pages = self._discover_pages(soup, final_url or self.url)
            for p in pages:
                if p not in getattr(self, '_visited_urls', set()):
                    pass
            self._crawl_pages(final_url or self.url, max_pages=max_pages)

        # Step 5: Create README
        self.create_readme(resources)
        
        # Summary
        print("\n" + "=" * 70)
        print("✅ CLONING COMPLETE!")
        print("=" * 70)
        print(f"\n📁 Your cloned website is ready in: {self.output_dir}/")
        print(f"📄 Main file: {self.output_dir}/index.html")
        print(f"\n💡 Quick start:")
        print(f"   open {self.output_dir}/index.html")
        print(f"\n🚀 Or run a local server:")
        print(f"   cd {self.output_dir} && python -m http.server 8000")
        
        if self.failed_downloads:
            print(f"\n⚠️  {len(self.failed_downloads)} resources failed to download")
            print(f"   (This is normal for external resources)")
        
        print("\n" + "─" * 70)
        print("💙 Enjoying WebClone? Star us on GitHub!")
        print("   https://github.com/AbdirahmanNomad/webclone")
        print("─" * 70 + "\n")
        
        return True


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python universal_clone.py <url> [output_directory]")
        print("\nExamples:")
        print("  python universal_clone.py https://example.com")
        print("  python universal_clone.py https://example.com my_site")
        sys.exit(1)
    
    url = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    
    cloner = UniversalWebsiteCloner(url, output_dir)
    success = cloner.clone()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
