"""
>>> repo().get_current_version()
'...'
>>> isinstance(repo(), Repo)
True
"""

from .base import Repo
from .subprocess import Git, Mercurial

__all__ = ['Repo', 'repo', 'Mercurial', 'Git']

repo = Repo.detect
