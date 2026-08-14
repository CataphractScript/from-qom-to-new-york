#!/usr/bin/env python3
"""Main entry point for the Qom Metro Transit Optimization Platform.

Usage:
    python main.py                          # Launch interactive shell
    python main.py --help                   # Show available subcommands
    python main.py route -s "Haram Motahhar Hazrat Masoumeh" -t "Pardisan" --algo astar
    python main.py mst --algo compare
    python main.py benchmark
"""

import sys
from pathlib import Path

# Add src to module search path
PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from from_qom_to_new_york.cli.app import main

if __name__ == "__main__":
    sys.exit(main())
