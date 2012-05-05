from __future__ import absolute_import

from . import base

try:
	import mercurial.__version__
	import mercurial.hg
	import mercurial.ui
	import mercurial.cmdutil
	import mercurial.util
	import mercurial.error
except ImportError:
	pass

class LibraryManager(base.HGRepoManager):
	"""
	An HGRepoManager implemented by exercising the mercurial Python APIs
	directly.

	Requires mercurial >= 1.2.
	"""

	def is_valid(self):
		modules_present = 'mercurial' in globals() and self.version_match()
		return modules_present and super(LibraryManager, self).is_valid()

	def find_root(self):
		try:
			return self.repo.root
		except Exception:
			pass

	def version_match(self):
		return mercurial.__version__.version >= '1.2'

	def _get_repo(self):
		class quiet_ui(mercurial.ui.ui):
			def write_err(self, *args, **kwargs):
				pass
		return mercurial.hg.repository(quiet_ui(), path=self.location)

	@property
	def repo(self):
		if not hasattr(self, '_repo'):
			self._repo = self._get_repo()
		return self._repo

	def _get_excluded(self):
		"""
		Return all files that hg knows about, but haven't been added,
		deleted, or removed or have an unknown status.
		"""
		modified, added, removed, deleted, unknown = self.repo.status()[:5]
		return removed + deleted + unknown

	def find_files(self):
		"""
		Use the Mercurial library to recursively find versioned files in dirname.
		"""
		excluded = self._get_excluded()
		rev = None
		match = mercurial.cmdutil.match(self.repo, [], {}, default='relglob')
		match.bad = lambda x, y: False
		return (abs
			for abs in self.repo[rev].walk(match)
			if (rev or abs in self.repo.dirstate)
			and abs not in excluded
			)
