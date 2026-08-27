from __future__ import annotations

import datetime

from stemma_detect import __version__

project = "Adafruit STEMMA Detect"
author = "Adafruit Industries"
copyright = f"2026-{datetime.datetime.now().year}, Adafruit Industries"
version = release = __version__

extensions = ["sphinx.ext.autodoc", "sphinx.ext.napoleon"]
templates_path = []
exclude_patterns = ["_build"]

html_theme = "sphinx_rtd_theme"
