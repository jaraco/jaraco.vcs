"""
>>> repo().get_current_version()
'...'
>>> isinstance(repo(), Repo)
True
"""

from .base import Repo
from .subprocess import Mercurial, Git


__all__ = ['Repo', 'repo']

repo = Repo.detect

# for compatibility
RepoManager = Repo
MercurialManager = Mercurial
GitManager = Git
