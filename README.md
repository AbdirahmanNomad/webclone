# 🌐 WebClone

> Clone any website in seconds. Perfect for learning, prototyping, and building.

[![PyPI version](https://badge.fury.io/py/webclone-cli.svg)](https://badge.fury.io/py/webclone-cli)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)

WebClone is a powerful command-line tool that creates local copies of websites, downloading all HTML, CSS, JavaScript, images, and fonts.

**Perfect for:** Learning web development, studying designs, creating prototypes, and building templates.

> ⚠️ **For educational use only.** Respect copyright laws. See [Legal Disclaimer](LEGAL.md).

---

## 📦 Installation

```bash
pip install webclone-cli
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

- 🚀 **One-Command Cloning** - Clone any website instantly
- 📦 **Smart Resource Management** - Auto-downloads all assets
- 🎨 **Preserves Design** - Maintains styling and animations
- 🔧 **Intelligent Path Fixing** - Updates paths to work locally
- 📝 **Auto Documentation** - Generates README for each clone
- 🎯 **Perfect for Learning** - Study how top sites are built

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

- External CDN resources may fail to download
- Dynamic content needs JavaScript to load
- Check browser DevTools (F12) → Console for errors

### Looks different from original?

- Server-side rendered content won't clone
- Database/CMS content needs backend
- Works best with client-side rendered sites

---

## 📂 Output Structure

```
your_cloned_site/
├── index.html              # Main HTML file
├── README.md              # Auto-generated docs
└── assets/
    ├── css/               # Stylesheets
    ├── js/                # JavaScript files
    ├── images/            # Images
    ├── fonts/             # Web fonts
    └── files/             # Other assets
```

---

## 🛠️ Requirements

- Python 3.7+
- Internet connection
- Dependencies (auto-installed):
  - requests
  - beautifulsoup4
  - lxml

---

## 📋 Command Options

```bash
webclone <url> [output_directory]

Arguments:
  url                  Website URL to clone
  output_directory     Optional custom folder name
```

---

## 🤝 Contributing

Contributions welcome! 

```bash
git clone https://github.com/AbdirahmanNomad/webclone.git
cd webclone
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
