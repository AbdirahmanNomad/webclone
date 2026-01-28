from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="webclone",
    version="1.0.0",
    author="Abdirahman Ahmed",
    author_email="contact@abdirahman.net",
    description="Clone any website in seconds. Perfect for learning, prototyping, and building.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AbdirahmanNomad/webclone",
    project_urls={
        "Bug Tracker": "https://github.com/AbdirahmanNomad/webclone/issues",
        "Documentation": "https://github.com/AbdirahmanNomad/webclone#readme",
        "Source Code": "https://github.com/AbdirahmanNomad/webclone",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
        "beautifulsoup4>=4.9.0",
        "lxml>=4.6.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.9",
            "mypy>=0.900",
        ],
    },
    entry_points={
        "console_scripts": [
            "webclone=webclone.cli:main",
        ],
    },
    keywords="web scraping, website cloner, web development, prototyping, html, css, javascript",
    include_package_data=True,
    zip_safe=False,
)
