"""Compatibility entry point: sizing controls now live in main-page settings."""
import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).with_name("test_settings.py")), run_name="__main__")
