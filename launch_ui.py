#!/usr/bin/env python3
"""Launch the Machine Context Engine Dashboard."""
import sys
import io

# Fix Unicode on Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from app.ui.dashboard import run_dashboard


if __name__ == "__main__":
    run_dashboard()
