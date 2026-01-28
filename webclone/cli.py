#!/usr/bin/env python3
"""
WebClone CLI - Command line interface for website cloning
"""

import sys
from .cloner import UniversalWebsiteCloner


def main():
    """Main CLI entry point"""
    if len(sys.argv) < 2:
        print("WebClone v1.0.0 - Clone any website in seconds")
        print("\nUsage: webclone <url> [output_directory]")
        print("\nExamples:")
        print("  webclone https://example.com")
        print("  webclone https://example.com my_site")
        print("\nFor more info: https://github.com/AbdirahmanNomad/webclone")
        sys.exit(1)
    
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
