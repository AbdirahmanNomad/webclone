# 🌐 WebClone

> Clone any website in seconds. Perfect for learning, prototyping, and building.

[![PyPI version](https://badge.fury.io/py/webclone-cli.svg)](https://badge.fury.io/py/webclone-cli)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

WebClone is a command-line tool that creates **local, mostly offline** copies of web pages: it saves HTML, CSS, JavaScript, images, fonts, and related assets, then rewrites paths so you can open the result from disk or a small static server.

**Perfect for:** Learning web development, studying designs, creating prototypes, and building templates.

### How it works (under the hood)

1. **Playwright (Chromium)** loads your URL so **JavaScript-rendered** content is included in the HTML snapshot.
2. **Light + dark capture** — two browser passes merge network activity so **`prefers-color-scheme: dark`** stylesheets and assets load, and the saved HTML comes from the **dark** pass (with common `dark` / `data-theme` hooks on `<html>`).
3. **HTML parsing** pulls `link`, `script`, `img`, `srcset`, lazy `data-src`, icons, inline `<style>` `url(...)`, etc.
4. **Recursive crawling** — follows every internal `<a href>` to discover and download ALL site pages (homepage, sub-pages, blog posts, etc.), not just the entry URL.
5. **Module chunk discovery** — finds all `<link rel="modulepreload">` and `<script type="module">` entries to download dynamically-loaded JS chunks.
6. **Build path preservation** — `_nuxt/`, `_next/`, `cms/`, `css/`, `fonts/` paths stay exactly as the server served them so framework dynamic imports keep working offline.
7. **Extra downloads** from **responses the browser actually made** (fonts, chunks, images that never appear as plain tags).
8. **CSS follow-up** walks downloaded stylesheets for **`url(...)`** and **`@import`**, downloads nested assets, and rewrites paths.
9. A final pass **replaces known remote URLs** in HTML and `*.css` with local paths where possible.
10. Falls back to a plain **HTTP** fetch if Playwright is unavailable or errors.

> ⚠️ **For educational use only.** Respect copyright laws. See [Legal Disclaimer](LEGAL.md).

---

## 📦 Installation

```bash
pip install webclone-cli
playwright install chromium
```

## 🚀 Quick Start

```bash
# Clone any website
webclone https://example.com

# Clone with custom name
webclone https://stripe.com stripe_clone

# View the result
cd example_com_cloned
python -m http.server 8000
# Visit http://localhost:8000
```

---

## ✨ Features

- 🚀 **One command** — `webclone <url> [folder]`
- 🕷️ **Recursive crawling** — Follows internal links and downloads ALL pages (like wget --mirror)
- 🎭 **Headless browser render** — Snapshots the DOM after JS runs (Playwright Chromium)
- 📡 **Fetch/XHR recording** — Captures runtime API calls as JSON files for offline use
- 🧩 **Framework route interception** — Detects Nuxt `_payload`, Next `_next/data`, Astro islands, SW manifests
- 📦 **Service Worker capture** — Saves sw.js, workbox bundles, webmanifest
- 💾 **Browser storage export** — Exports localStorage, sessionStorage, cookies
- 🔄 **DOM mutation observer** — Waits for SPA content to stabilize before snapshot
- 📜 **Infinite scroll detection** — Scrolls until height stops growing (blogs, feeds, docs)
- 🖼️ **Iframe capture** — Clones same-origin iframes inline
- 📊 **HAR export** — Saves network.har for debugging failed clones
- 🌙 **Dark theme aware** — Light + dark passes for complete asset capture
- 📦 **CSS deep crawl** — Follows `url(...)` and `@import` inside stylesheets
- 🔧 **Build path preservation** — Keeps `_nuxt/`, `_next/`, `cms/` paths intact
- 🧩 **Module chunk discovery** — Finds `modulepreload` and lazy-loaded JS
- 🔧 **Local path rewriting** — Points HTML/CSS at downloaded files
- 📝 **Per-clone README** — Auto-generated docs with asset counts
- 🎯 **Great for learning** — Inspect real layouts, typography, and structure offline

---

## 💡 What Works Best

### ✅ Great Results With:
- **Static Sites** - Landing pages, portfolios (Docker.com, Stripe.com)
- **Client-Side Apps** - React, Vue, Next.js apps (Vercel.com, Linear.app)
- **Documentation** - Docs sites, wikis, guides
- **Marketing Pages** - Product pages, company sites

### ⚠️ Limited Support:
- **CMS Sites** - WordPress, Umbraco (clones design, not backend)
- **Server-Side Apps** - PHP, ASP.NET (visual shell only)
- **API-Heavy Apps** - Dynamic dashboards (layout only)

**Still useful for:** Studying designs, extracting UI components, learning CSS structures.

[Learn more about what can/cannot be cloned →](https://github.com/AbdirahmanNomad/webclone#what-works-best)

---

## 📖 Usage Examples

### Learning from top companies:
```bash
webclone https://www.stripe.com
webclone https://www.linear.app
webclone https://vercel.com
```

### Building prototypes:
```bash
webclone https://landing-template.com my_project
# Edit the HTML/CSS to customize
```

### Studying documentation:
```bash
webclone https://docs.docker.com docker_docs
```

---

## 🔧 Troubleshooting

### Website shows raw HTML?

**Problem:** JavaScript won't run when opened directly (file://)

**Solution:** Use a local server:
```bash
cd your_cloned_site
python3 -m http.server 8000
# Visit http://localhost:8000
```

### Missing images or styles?

- External CDN resources may fail to download (CORS, auth, signed URLs)
- Some assets load only after **user interaction** or **infinite scroll** — clone again after scrolling the live site, or accept gaps
- **Analytics / POST-only** URLs in the network list may “fail” on GET — harmless
- Check browser DevTools (F12) → Console when viewing the clone

### Cloudflare or bot protection?

Sites behind **Cloudflare / aggressive bot checks** may block headless Chromium or return challenge pages. There is **no guaranteed bypass**. Options: use content you’re **allowed** to archive (API, export, staging), or complete a challenge in a normal browser and explore **cookie / session** workflows yourself if appropriate.

### Looks different from original?

- Server-side rendered content won't clone
- Database/CMS content needs backend
- Works best with client-side rendered sites

---

## 📂 Output Structure

```
your_cloned_site/
├── index.html              # Main HTML file
├── page1.html              # Crawled pages
├── page2/
│   └── index.html          # Nested pages
├── README.md               # Auto-generated docs
├── _nuxt/                  # Framework build files (preserved as-is)
├── _next/                  # Next.js build files (preserved as-is)
├── cms/                    # CMS assets (preserved as-is)
└── assets/
    ├── css/               # Stylesheets
    ├── js/                # JavaScript files
    ├── images/            # Images
    ├── fonts/             # Web fonts
    └── files/             # Other assets
```

---

## 🛠️ Requirements

- Python 3.8+
- Internet connection
- Chromium for Playwright (one-time after install): `playwright install chromium`
- Dependencies (auto-installed):
  - requests
  - beautifulsoup4
  - lxml
  - playwright (renders the page so JS-heavy sites clone better; assets still downloaded by WebClone)

---

## 📋 Command Options

```bash
webclone <url> [output_directory]

Arguments:
  url                  Website URL to clone
  output_directory     Optional custom folder name (default: <host>_cloned)
```

There are **no subcommands or flags** — one URL, one optional output folder.

---

## 🤝 Contributing

Contributions welcome! 

```bash
git clone https://github.com/AbdirahmanNomad/webclone.git
cd webclone
pip install -r requirements.txt
playwright install chromium
pip install -e ".[dev]"
```

---

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## ⚠️ Important Notice

**For educational purposes only.** 

- ✅ Learning and personal projects
- ✅ Design inspiration and research
- ❌ Commercial use without permission
- ❌ Copyright infringement

**Users are responsible for respecting copyright laws.** See full [Legal Disclaimer](LEGAL.md).

---

## 👤 Author

**Abdirahman Ahmed**

- Website: [abdirahman.net](https://www.abdirahman.net)
- GitHub: [@AbdirahmanNomad](https://github.com/AbdirahmanNomad)
- PyPI: [webclone-cli](https://pypi.org/project/webclone-cli/)

---

## 📈 Support

Give a ⭐️ if this project helped you!

- [Report Issues](https://github.com/AbdirahmanNomad/webclone/issues)
- [View on PyPI](https://pypi.org/project/webclone-cli/)
- Share with #WebClone

---

<p align="center">Made with ❤️ for developers learning web development</p>
