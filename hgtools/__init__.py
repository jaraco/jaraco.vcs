"""
Module for the hgtools package

Credit to Jannis Leidel for setuptools_hg from which hgtools was forked.
"""

# kept for backward compatibility - will be removed in 0.7 or 0.8
from .plugins import (
	version_calc as version_calc_plugin,
	file_finder as file_finder_plugin,
	)

