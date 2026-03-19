#!/usr/bin/env python3
"""Standalone entry point for source intake. Delegates to intake_runner."""

import sys
from pathlib import Path

# Ensure project root is on sys.path when run as standalone script
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from oil_painting_rag.ingestion.intake_runner import main

if __name__ == "__main__":
    main()
