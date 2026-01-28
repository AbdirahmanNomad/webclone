# 🌐 WebClone

> Clone any website in seconds. Perfect for learning, prototyping, and building.

[![PyPI version](https://badge.fury.io/py/webclone.svg)](https://badge.fury.io/py/webclone)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)

WebClone is a powerful command-line tool that creates perfect clones of any website, downloading all HTML, CSS, JavaScript, images, and fonts while organizing everything intelligently.

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
pip install webclone
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

## ⚠️ Disclaimer

WebClone is intended for:
- ✅ Learning and education
- ✅ Personal prototyping
- ✅ Design inspiration
- ✅ With permission for client work

Please respect:
- ❌ Copyright and intellectual property
- ❌ Terms of service of websites
- ❌ Privacy and data protection laws

Always get permission before using cloned content publicly or commercially.

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
