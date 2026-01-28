# 📦 Publishing WebClone to PyPI

## Prerequisites

```bash
pip install build twine
```

## Steps to Publish

### 1. Test Locally

```bash
cd webclone_package
pip install -e .
webclone https://example.com test_clone
```

### 2. Build the Package

```bash
python -m build
```

This creates:
- `dist/webclone-1.0.0.tar.gz`
- `dist/webclone-1.0.0-py3-none-any.whl`

### 3. Test on TestPyPI (Optional but Recommended)

```bash
# Upload to TestPyPI
python -m twine upload --repository testpypi dist/*

# Test install
pip install --index-url https://test.pypi.org/simple/ webclone
```

### 4. Publish to PyPI

```bash
python -m twine upload dist/*
```

You'll be asked for your PyPI credentials.

### 5. Install from PyPI

```bash
pip install webclone
```

## GitHub Release Steps

### 1. Commit Everything

```bash
git add .
git commit -m "Initial release v1.0.0"
```

### 2. Create Tag

```bash
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin main
git push origin v1.0.0
```

### 3. Create GitHub Release

1. Go to https://github.com/AbdirahmanNomad/webclone/releases
2. Click "Create a new release"
3. Choose tag `v1.0.0`
4. Title: `WebClone v1.0.0 - Initial Release`
5. Description:
   ```markdown
   🎉 First stable release of WebClone!

   ## Features
   - Clone any website with one command
   - Smart resource organization
   - Auto documentation generation
   - Cross-platform support

   ## Installation
   ```bash
   pip install webclone
   ```

   ## Quick Start
   ```bash
   webclone https://example.com
   ```

   ## What's New
   - Initial public release
   - Full PyPI package
   - Comprehensive documentation
   ```
6. Attach the dist files (`.tar.gz` and `.whl`)
7. Click "Publish release"

## Update PyPI Credentials

Create `~/.pypirc`:

```ini
[pypi]
username = __token__
password = pypi-YOUR_TOKEN_HERE

[testpypi]
username = __token__
password = pypi-YOUR_TEST_TOKEN_HERE
```

Get tokens from:
- PyPI: https://pypi.org/manage/account/token/
- TestPyPI: https://test.pypi.org/manage/account/token/

## Version Bumping (Future Releases)

1. Update version in `setup.py`
2. Update version in `webclone/__init__.py`
3. Update CHANGELOG.md
4. Commit, tag, and publish

```bash
# Example for v1.1.0
git commit -m "Bump version to 1.1.0"
git tag -a v1.1.0 -m "Release version 1.1.0"
git push origin main --tags
python -m build
python -m twine upload dist/*
```

## Checklist Before Publishing

- [ ] All tests pass
- [ ] README is complete
- [ ] LICENSE is included
- [ ] requirements.txt is accurate
- [ ] Version numbers match
- [ ] CHANGELOG is updated
- [ ] Examples work
- [ ] Package builds without errors
- [ ] TestPyPI upload works
- [ ] GitHub repo is public

## Post-Publishing

1. **Announce on Social Media**
   - Twitter/X with #Python #WebDev #OpenSource
   - LinkedIn
   - Dev.to article
   - Reddit (r/Python, r/webdev)

2. **Submit to Lists**
   - Awesome Python lists
   - Product Hunt
   - Hacker News

3. **Update Portfolio**
   - Add to abdirahman.net
   - Update GitHub profile README

## Support

For issues: https://github.com/AbdirahmanNomad/webclone/issues
