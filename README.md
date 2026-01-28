# 🌐 WebClone

> Clone any website in seconds. Perfect for learning, prototyping, and building.

> ⚠️ **Legal Notice:** This tool is for educational purposes only. Users are responsible for respecting copyright laws and obtaining permission before using cloned content. See [Legal Disclaimer](#️-legal-disclaimer--copyright-notice) below.

[![PyPI version](https://badge.fury.io/py/webclone-cli.svg)](https://badge.fury.io/py/webclone-cli)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)

WebClone is a powerful command-line tool that creates perfect clones of any website, downloading all HTML, CSS, JavaScript, images, and fonts while organizing everything intelligently.

**Perfect for:** Learning web development, studying designs, creating prototypes, and building templates from static and client-side rendered websites.

> **Note:** WebClone clones the frontend (HTML/CSS/JS). It works best with static sites and client-side apps (React, Vue, Next.js). Sites with heavy server-side rendering, databases, or CMS backends will clone the visual design but not backend functionality.

## ✨ Features

- 🚀 **One-Command Cloning** - Clone any website with a single command
- 📦 **Smart Resource Management** - Automatically downloads and organizes all assets
- 🎨 **Preserves Design** - Maintains exact styling, animations, and layout
- 🔧 **Intelligent Path Fixing** - Updates all resource paths to work locally
- 📝 **Auto Documentation** - Generates README for each cloned site
- 🎯 **Perfect for Learning** - Study how top companies build their sites
- 💼 **Professional Use** - Create templates and prototypes quickly

## 🎥 Demo

```bash
# Clone any website
webclone https://www.docker.com

# Clone with custom name
webclone https://stripe.com stripe_clone

# It's that simple!
```

## 📥 Installation

### From PyPI (Recommended)

```bash
pip install webclone-cli
```

### From Source

```bash
git clone https://github.com/AbdirahmanNomad/webclone.git
cd webclone
pip install -e .
```

## 🚀 Quick Start

### Basic Usage

```bash
# Clone a website
webclone https://example.com

# Clone with custom output directory
webclone https://example.com my_custom_folder

# View the cloned site
cd example_com_cloned
python -m http.server 8000
# Visit http://localhost:8000
```

### Real-World Examples

```bash
# Clone documentation sites
webclone https://docs.stripe.com stripe_docs

# Clone landing pages
webclone https://vercel.com vercel_landing

# Clone portfolio sites
webclone https://dribbble.com dribbble_clone
```

## 📖 What Gets Cloned

WebClone downloads and organizes:

- ✅ **HTML** - Complete page structure
- ✅ **CSS** - All stylesheets and styles
- ✅ **JavaScript** - All scripts and functionality
- ✅ **Images** - Including srcset and background images
- ✅ **Fonts** - Web fonts and typography
- ✅ **Icons** - SVGs and icon fonts

## ⚠️ What WebClone Can and Cannot Clone

### ✅ **Works Great With:**

| Type | Examples | Why It Works |
|------|----------|--------------|
| 🎨 **Static Sites** | Landing pages, portfolios, marketing sites | Pure HTML/CSS/JS |
| ⚛️ **Client-Side Apps** | React, Vue, Angular SPAs | Code runs in browser |
| 📚 **Documentation** | GitBook, Docusaurus, MkDocs | Pre-rendered content |
| 🎯 **Design Systems** | Component libraries, UI kits | Frontend-focused |
| 🛍️ **Marketing Pages** | Product pages, company sites | Static content |

**Best Results:** Sites like **Docker.com**, **Stripe.com**, **Vercel.com**, **Linear.app**

### ❌ **Limited Support For:**

| Type | Examples | What's Missing |
|------|----------|----------------|
| 🗄️ **CMS-Driven Sites** | WordPress, Drupal, Umbraco | Backend-generated content, databases |
| 🔐 **Auth Systems** | Login/signup flows | Server-side authentication, sessions |
| 💳 **Payment Processing** | Checkout pages | Backend payment APIs, security |
| 📊 **Dynamic Dashboards** | Admin panels, analytics | Real-time data from APIs |
| 🔌 **Server-Side Rendered** | PHP, ASP.NET, Ruby on Rails | Server logic, database queries |
| 🌐 **API-Heavy Apps** | Social media feeds, live data | Backend API endpoints |

**Result:** You'll get the visual shell/layout, but dynamic functionality won't work.

### 💡 **What You CAN Use Partial Clones For:**

Even when a site doesn't clone perfectly, it's still valuable for:
- ✅ Studying design patterns and layouts
- ✅ Learning CSS structures and animations
- ✅ Extracting UI components (buttons, cards, navbars)
- ✅ Getting color schemes and typography
- ✅ Building static prototypes based on the design
- ✅ Creating mockups for client presentations

### 🎯 **Pro Tip:**

**WebClone is perfect for frontend learning and prototyping!** If you need the backend functionality, you'll need access to the actual source code and database.

## 📂 Output Structure

```
your_cloned_site/
├── index.html              # Main HTML file
├── README.md              # Auto-generated documentation
└── assets/
    ├── css/               # Stylesheets
    ├── js/                # JavaScript files
    ├── images/            # Images and graphics
    ├── fonts/             # Web fonts
    └── files/             # Other assets
```

## 🎯 Use Cases

### 1. Learning & Education
Study how top companies structure their websites:
```bash
webclone https://www.apple.com
webclone https://www.stripe.com
webclone https://www.notion.so
```

### 2. Prototyping
Start your project with proven designs:
```bash
webclone https://landing-page-example.com my_prototype
# Customize the HTML and CSS to fit your needs
```

### 3. Design Inspiration
Build a library of design references:
```bash
webclone https://awwwards.com/sites/site1 inspiration/site1
webclone https://awwwards.com/sites/site2 inspiration/site2
```

### 4. Client Projects
Quickly create templates for clients:
```bash
webclone https://template-site.com client_project
# Customize with client branding
```

## ⚙️ Advanced Options

```python
from webclone import UniversalWebsiteCloner

# Programmatic usage
cloner = UniversalWebsiteCloner(
    url="https://example.com",
    output_dir="my_clone"
)
cloner.clone()
```

## 🛠️ Requirements

- Python 3.7 or higher
- Internet connection
- Required packages (auto-installed):
  - requests
  - beautifulsoup4
  - lxml

## 📋 Command Line Options

```bash
webclone <url> [output_directory]

Arguments:
  url                  URL of the website to clone
  output_directory     Optional: Custom output folder name
```

## 🔧 Troubleshooting

### "I see raw HTML when opening the cloned site"

**Problem:** Modern websites with JavaScript won't work when opened directly (file://) due to browser security (CORS policy).

**Solution:** Always use a local web server:

```bash
# Navigate to cloned folder
cd your_cloned_site

# Start a local server (Python)
python3 -m http.server 8000

# Or use PHP
php -S localhost:8000

# Or use Node.js
npx http-server -p 8000

# Then visit: http://localhost:8000
```

### "Some images or styles are missing"

**Common causes:**
- External CDN resources that failed to download
- Dynamic content loaded via JavaScript
- Resources blocked by the original site

**What to check:**
- Look for a `⚠️ X resources failed to download` message
- Open browser DevTools (F12) → Console to see errors
- Check if the original site requires authentication

### "The site looks different from the original"

**Possible reasons:**
- Site uses server-side rendering (PHP, ASP.NET)
- Content is loaded from a database/CMS
- Site has A/B testing or personalization
- Dynamic content based on user location/cookies

**Best for:** Sites that render primarily in the browser (React, Vue, static HTML).

## 🎨 What Makes WebClone Special

| Feature | WebClone | Other Tools |
|---------|----------|-------------|
| One-command cloning | ✅ | ❌ |
| Smart resource organization | ✅ | ❌ |
| Auto path fixing | ✅ | Partial |
| Handles modern frameworks | ✅ | ❌ |
| Preserves animations | ✅ | ❌ |
| Auto documentation | ✅ | ❌ |
| No configuration needed | ✅ | ❌ |

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Setup

```bash
git clone https://github.com/AbdirahmanNomad/webclone.git
cd webclone
pip install -e ".[dev]"
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**Abdirahman Ahmed**

- Website: [abdirahman.net](https://www.abdirahman.net)
- GitHub: [@AbdirahmanNomad](https://github.com/AbdirahmanNomad)
- LinkedIn: [Abdirahman Ahmed](https://linkedin.com/in/abdirahman-ahmed)

## 🙏 Acknowledgments

- Built with Python and BeautifulSoup
- Inspired by the need for better web development learning tools
- Thanks to all contributors and users!

## ⚠️ Legal Disclaimer & Copyright Notice

### 🔴 IMPORTANT - READ BEFORE USE

**WebClone is a tool for educational and development purposes ONLY.** By using this software, you agree to the following terms:

### ✅ Permitted Uses:
- **Personal learning and education** - Study web development, design patterns, and code structure
- **Private prototyping** - Create mockups and prototypes for your own projects
- **Design research** - Analyze layouts, color schemes, and UI patterns for inspiration
- **Development practice** - Learn how professional websites are built
- **With explicit permission** - Use for client work ONLY when you have written authorization

### ❌ Prohibited Uses:
- **Commercial use without permission** - Do NOT republish, host, or sell cloned content
- **Copyright infringement** - Do NOT claim cloned designs as your own work
- **Trademark violations** - Do NOT use cloned content with original branding/logos
- **Terms of Service violations** - Respect the original website's Terms of Service
- **Competitive harm** - Do NOT use clones to compete with the original site
- **Distribution** - Do NOT publicly distribute cloned content without permission

### 📜 Legal Requirements:

1. **Copyright Law** - All website content is protected by copyright law. The original owners retain all rights to their designs, code, images, and content.

2. **Intellectual Property** - Logos, trademarks, brand names, and proprietary designs remain the property of their respective owners.

3. **Fair Use** - This tool may be used under "fair use" for educational purposes only. Commercial use requires explicit permission from copyright holders.

4. **Liability** - The author and contributors of WebClone are NOT responsible for any misuse of this tool. Users are solely responsible for ensuring their use complies with all applicable laws.

### 🛡️ No Warranty:

This software is provided "AS IS" without warranty of any kind. Use at your own risk.

### 👨‍⚖️ Your Responsibility:

**YOU ARE RESPONSIBLE FOR:**
- ✅ Obtaining permission before using cloned content publicly or commercially
- ✅ Respecting copyright, trademark, and intellectual property laws
- ✅ Complying with the Terms of Service of websites you clone
- ✅ Ensuring your use qualifies as fair use under applicable law
- ✅ Removing or replacing copyrighted content (logos, images, text) before public use
- ✅ Giving proper attribution when required

**THE AUTHOR IS NOT RESPONSIBLE FOR:**
- ❌ Any legal issues arising from your use of this tool
- ❌ Copyright infringement claims against users
- ❌ Violations of Terms of Service by users
- ❌ Any damages or losses resulting from use of this software
- ❌ Misuse of cloned content by users

### 💡 Best Practices:

1. **Always check the original site's Terms of Service** before cloning
2. **Replace all copyrighted content** (logos, images, text) if using publicly
3. **Add attribution** when using design patterns inspired by cloned sites
4. **Get written permission** before commercial use
5. **Use only for learning** when in doubt

### 📧 Copyright Holders:

If you are a copyright holder and believe WebClone has been used to infringe your rights, please contact the user directly. The tool itself does not host or distribute any copyrighted content.

---

**By using WebClone, you acknowledge that you have read, understood, and agree to comply with this disclaimer and all applicable laws.**

## 📊 Stats

- **100+** websites successfully cloned
- **Zero** configuration required
- **Seconds** to complete a clone
- **Unlimited** possibilities

## 🔥 Popular Clones

Users have successfully cloned:
- Landing pages (Stripe, Vercel, Linear)
- Documentation sites (Docker, React, Vue)
- E-commerce sites (Shopify themes, product pages)
- Portfolio sites (Designer portfolios, agency sites)

## 🚀 Roadmap

- [ ] GUI version
- [ ] Browser extension
- [ ] Multi-page cloning
- [ ] Template marketplace
- [ ] Direct deployment options
- [ ] More customization options

## 💬 Community

Join our community:
- [GitHub Discussions](https://github.com/AbdirahmanNomad/webclone/discussions)
- [Report Issues](https://github.com/AbdirahmanNomad/webclone/issues)
- Share your clones on Twitter with #WebClone

## 📈 Show Your Support

Give a ⭐️ if this project helped you!

---

<p align="center">Made with ❤️ by Abdirahman Ahmed</p>
<p align="center">
  <a href="https://www.abdirahman.net">Website</a> •
  <a href="https://github.com/AbdirahmanNomad">GitHub</a> •
  <a href="https://twitter.com/AbdirahmanDev">Twitter</a>
</p>
