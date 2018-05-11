"""
hgtools implements several repo managers, each of which provides an interface
to Mercurial functionality.
"""

import posixpath
import itertools

from more_itertools import one
from jaraco.classes.ancestry import iter_subclasses

from .. import versioning


class RepoManager(versioning.VersionManagement):
	"""
	An abstract class defining some interfaces for working with
	repositories.
	"""
	def __init__(self, location='.'):
		self.location = location
		self.setup()

	def is_valid(self):
		"Return True if this is a valid manager for this location."
		return True

	def setup(self):
		pass

	@classmethod
	def get_valid_managers(cls, location):
		"""
		Get the valid RepoManagers for this location.
		"""
		def by_priority_attr(c):
			return getattr(c, 'priority', 0)
		classes = sorted(
			iter_subclasses(cls), key=by_priority_attr,
			reverse=True)
		all_managers = (c(location) for c in classes)
		return (mgr for mgr in all_managers if mgr.is_valid())

	@staticmethod
	def get_first_valid_manager(location='.'):
		try:
			return next(RepoManager.get_valid_managers(location))
		except StopIteration as e:
			e.args = "No source repo or suitable VCS version found",
			raise

	@staticmethod
	def existing_only(managers):
		"""
		Return only those managers that refer to an existing repo
		"""
		return (mgr for mgr in managers if mgr.find_root())

	def __repr__(self):
		return '{self.__class__.__name__}({self.location})'.format(**vars())

	def find_root(self):
		raise NotImplementedError()

	def find_files(self):
		raise NotImplementedError()

	def get_tags(self, rev=None):
		"""
		Get the tags for the specified revision (or the current revision
		if none is specified).
		"""
		raise NotImplementedError()

	def get_repo_tags(self):
		"""
		Get all tags for the repository.
		"""
		raise NotImplementedError()

	def get_parent_tags(self, rev=None):
		"""
		Return the tags for the parent revision (or None if no single
			parent can be identified).
		"""
		try:
			parent_rev = one(self.get_parent_revs(rev))
		except Exception:
			return None
		return self.get_tags(parent_rev)

	def get_parent_revs(self, rev=None):
		"""
		Get the parent revision for the specified revision (or the current
		revision if none is specified).
		"""
		raise NotImplementedError

	def is_modified(self):
		'Does the current working copy have modifications'
		raise NotImplementedError()

	def find_all_files(self):
		"""
		Find files including those in subrepositories.
		"""
		files = self.find_files()
		subrepo_files = (
			posixpath.join(subrepo.location, filename)
			for subrepo in self.subrepos()
			for filename in subrepo.find_files()
		)
		return itertools.chain(files, subrepo_files)

	def subrepos(self):
		try:
			with open(posixpath.join(self.location, '.hgsub')) as file:
				subs = list(file)
		except Exception:
			subs = []

		locs = [part.partition('=')[0].strip() for part in subs]
		return [self.__class__(posixpath.join(self.location, loc)) for loc in locs]
