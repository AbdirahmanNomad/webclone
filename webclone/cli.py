#!/usr/bin/env python3
"""
WebClone CLI - Command line interface for website cloning
"""

import sys

from .cloner import UniversalWebsiteCloner
from .serve import serve


def main():
    """Main CLI entry point"""
    if len(sys.argv) < 2:
        print("WebClone v2.0.0 - Clone any website + offline replay server")
        print("\nUsage:")
        print("  webclone <url> [output_directory]   # Clone a website")
        print("  webclone serve <clone_directory>     # Start replay server")
        print("\nExamples:")
        print("  webclone https://example.com")
        print("  webclone https://example.com my_site")
        print("  webclone serve my_site              # Serve at http://localhost:8000")
        print("\nFor more info: https://github.com/AbdirahmanNomad/webclone")
        sys.exit(1)

    command = sys.argv[1]

    if command == "serve":
        clone_dir = sys.argv[2] if len(sys.argv) > 2 else "."
        port = int(sys.argv[3]) if len(sys.argv) > 3 else 8000
        serve(clone_dir, port)
        return

    # Default: clone
    url = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        cloner = UniversalWebsiteCloner(url, output_dir)
        success = cloner.clone()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nCloning cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
