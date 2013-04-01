import sys as _sys

from .base import HGRepoManager
from .subprocess import SubprocessManager

if _sys.version_info >= (2, 7):
	from .library import LibraryManager
