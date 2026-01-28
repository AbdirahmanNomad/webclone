#!/usr/bin/env python3
"""
Universal Website Cloner
Clone any website with its complete design, styles, scripts, and assets.
Can be used for any future projects.

Usage:
    python universal_clone.py <url> [output_directory]
    
Example:
    python universal_clone.py https://example.com my_cloned_site
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
        
    def _get_base_url(self, url):
        """Get base URL for the site"""
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"
    
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
        """Fetch HTML page"""
        if url is None:
            url = self.url
            
        try:
            print(f"Fetching {url}...")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            print("✓ Successfully fetched page")
            return response.text, response.url
        except Exception as e:
            print(f"✗ Error fetching page: {e}")
            return None, None
    
    def _get_file_extension(self, url, content_type=None):
        """Determine file extension from URL or content type"""
        parsed = urlparse(url)
        path = parsed.path
        
        # Try to get extension from URL
        if '.' in path.split('/')[-1]:
            return path.split('.')[-1].lower()
        
        # Fallback to content type
        if content_type:
            extensions = {
                'text/css': 'css',
                'text/javascript': 'js',
                'application/javascript': 'js',
                'application/json': 'json',
                'image/jpeg': 'jpg',
                'image/png': 'png',
                'image/gif': 'gif',
                'image/svg+xml': 'svg',
                'image/webp': 'webp',
                'font/woff': 'woff',
                'font/woff2': 'woff2',
                'font/ttf': 'ttf',
                'font/otf': 'otf',
            }
            return extensions.get(content_type, 'bin')
        
        return 'bin'
    
    def _get_local_path(self, url, resource_type='file'):
        """Generate local path for a resource"""
        # If already downloaded, return cached path
        if url in self.downloaded_files:
            return self.downloaded_files[url]
        
        parsed = urlparse(url)
        path = parsed.path.lstrip('/')
        
        # Handle empty paths
        if not path or path.endswith('/'):
            path = path + 'index.html'
        
        # Create subdirectory based on resource type
        type_dirs = {
            'css': 'assets/css',
            'js': 'assets/js',
            'image': 'assets/images',
            'font': 'assets/fonts',
            'file': 'assets/files',
        }
        
        # If path doesn't have proper structure, organize by type
        if resource_type in type_dirs and not path.startswith(('assets/', '_next/', 'static/')):
            filename = os.path.basename(path) or f"file_{hashlib.md5(url.encode()).hexdigest()[:8]}"
            path = f"{type_dirs[resource_type]}/{filename}"
        
        return path
    
    def download_resource(self, url, resource_type="file"):
        """Download a resource (CSS, JS, image, etc.)"""
        # Skip if already downloaded
        if url in self.downloaded_files:
            return self.downloaded_files[url]
        
        # Skip if previously failed
        if url in self.failed_downloads:
            return None
            
        try:
            # Handle relative URLs
            full_url = urljoin(self.base_url, url)
            
            # Skip data URLs
            if full_url.startswith('data:'):
                return None
            
            # Skip external domains for some resource types
            parsed_full = urlparse(full_url)
            parsed_base = urlparse(self.base_url)
            
            response = self.session.get(full_url, timeout=15, stream=True)
            response.raise_for_status()
            
            # Determine local path
            local_path = self._get_local_path(url, resource_type)
            full_local_path = os.path.join(self.output_dir, local_path)
            
            # Create subdirectories as needed
            os.makedirs(os.path.dirname(full_local_path), exist_ok=True)
            
            # Determine if binary or text
            content_type = response.headers.get('content-type', '').lower()
            is_binary = any(t in content_type for t in ['image', 'font', 'octet-stream', 'pdf'])
            
            # Save the file
            mode = 'wb' if is_binary else 'w'
            with open(full_local_path, mode) as f:
                if is_binary:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                else:
                    f.write(response.text)
            
            # Cache the local path
            self.downloaded_files[url] = local_path
            
            print(f"  ✓ {resource_type}: {os.path.basename(local_path)}")
            return local_path
            
        except Exception as e:
            print(f"  ✗ Failed {url}: {str(e)[:50]}")
            self.failed_downloads.append(url)
            return None
    
    def extract_and_download_resources(self, soup):
        """Extract and download all resources from HTML"""
        resources_downloaded = {
            'css': 0,
            'js': 0,
            'images': 0,
            'fonts': 0,
            'other': 0
        }
        
        print("\n📦 Downloading CSS files...")
        # CSS files
        for link in soup.find_all('link', rel='stylesheet'):
            if link.get('href'):
                if self.download_resource(link['href'], 'css'):
                    resources_downloaded['css'] += 1
        
        # Preload CSS
        for link in soup.find_all('link', rel='preload', as_='style'):
            if link.get('href'):
                if self.download_resource(link['href'], 'css'):
                    resources_downloaded['css'] += 1
        
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
        
        # Images with srcset
        for img in soup.find_all('img', srcset=True):
            srcset = img.get('srcset', '')
            urls = re.findall(r'(https?://[^\s,]+|/[^\s,]+)', srcset)
            for url in urls:
                if self.download_resource(url, 'image'):
                    resources_downloaded['images'] += 1
        
        # Background images in style attributes
        for elem in soup.find_all(style=True):
            style = elem['style']
            urls = re.findall(r'url\([\'"]?([^\'"]+)[\'"]?\)', style)
            for url in urls:
                if self.download_resource(url, 'image'):
                    resources_downloaded['images'] += 1
        
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
            if original_href in self.downloaded_files:
                link['href'] = self.downloaded_files[original_href]
        
        # Update scripts
        for script in soup.find_all('script', src=True):
            original_src = script['src']
            if original_src in self.downloaded_files:
                script['src'] = self.downloaded_files[original_src]
        
        # Update images
        for img in soup.find_all('img', src=True):
            original_src = img['src']
            if original_src in self.downloaded_files:
                img['src'] = self.downloaded_files[original_src]
        
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
    
    def save_html(self, html_content, final_url):
        """Save the processed HTML file"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Download all resources
        resources = self.extract_and_download_resources(soup)
        
        # Update paths to local files
        soup = self.update_resource_paths(soup)
        
        # Add critical CSS
        soup = self.add_critical_css(soup)
        
        # Add meta tag indicating this is a clone
        meta = soup.new_tag('meta', attrs={'name': 'cloned-from', 'content': self.url})
        if soup.head:
            soup.head.append(meta)
        
        # Save to index.html
        output_path = os.path.join(self.output_dir, 'index.html')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(str(soup.prettify()))
        
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
Generated by Universal Website Cloner
"""
        
        readme_path = os.path.join(self.output_dir, 'README.md')
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        print(f"✓ Created README: {readme_path}")
    
    def clone(self):
        """Main cloning process"""
        print("=" * 70)
        print("🌐 UNIVERSAL WEBSITE CLONER")
        print("=" * 70)
        print(f"Target URL: {self.url}")
        print(f"Output Dir: {self.output_dir}/")
        print("=" * 70)
        
        # Step 1: Create directory structure
        self.create_directory_structure()
        
        # Step 2: Fetch main HTML
        html_content, final_url = self.fetch_page()
        if not html_content:
            print("\n✗ Failed to fetch page. Aborting.")
            return False
        
        # Update base URL if redirected
        if final_url and final_url != self.url:
            self.base_url = self._get_base_url(final_url)
            print(f"ℹ️  Redirected to: {final_url}")
        
        # Step 3: Download resources and save HTML
        resources = self.save_html(html_content, final_url)
        
        # Step 4: Create README
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
