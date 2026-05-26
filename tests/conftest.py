"""Conftest for pytest — adds project root to sys.path."""

import os
import sys

# Add project root to Python path so imports like "from server import app" work
_proj_root = os.path.dirname(os.path.dirname(__file__))
if _proj_root not in sys.path:
    sys.path.insert(0, _proj_root)
