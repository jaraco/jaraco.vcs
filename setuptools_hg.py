"""
Classes for working with repositories using the Mercurial version
control system. Includes a plugin for setuptools to find files managed
by the version control system.

Classes support using the native Python library interfaces or using the
hg(1) command as a subprocess.
"""
__version__ = '0.3'
__author__ = 'Jannis Leidel'
__all__ = ['hg_file_finder']

import os
import subprocess

class HGRepoManager(object):
	def __init__(self, location='.'):
		self.location = location
		self.setup()

	def is_valid(self):
		return True

	def setup(self):
		pass

	@staticmethod
	def get_valid_managers(location):
		classes = (LibraryManager, LegacyLibraryManager, SubprocessManager)
		force_cmd = os.environ.get('HG_SETUPTOOLS_FORCE_CMD', False)
		if force_cmd:
			classes = (SubprocessManager, LibraryManager, LegacyLibraryManager)
		managers = (cls(location) for cls in classes)
		return (mgr for mgr in managers if mgr.is_valid())

	def __repr__(self):
		class_name = self.__class__.__name__
		loc = self.location
		return '%(class_name)s(%(loc)r)' % vars()

	def get_tag(self):
		raise NotImplementedError()

class SubprocessManager(HGRepoManager):
	exe = 'hg'

	def is_valid(self):
		return 0 == subprocess.call(
			[self.exe, 'version'],
			stdout=self._get_devnull(),
			)

	def _run_cmd(self, cmd):
		proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
			cwd=self.location)
		stdout, stderr = proc.communicate()
		return stdout

	def find_files(self):
		"""
		Find versioned files in self.location
		"""
		return self._run_cmd(['hg', 'locate']).splitlines()

	@staticmethod
	def _get_devnull():
		return open(os.path.devnull, 'w')

	def get_tag(self):
		return self._run_cmd(['hg', 'identify', '-t']).strip() or None

class LibraryManager(HGRepoManager):
	OLD_VERSIONS = ('1.0', '1.0.1', '1.0.2')

	def setup(self):
		try:
			from mercurial.__version__ import version
			from mercurial import hg, ui, cmdutil
		except ImportError:
			pass

		try:
			from mercurial.error import RepoError
		except ImportError:
			# mercurial < 1.2
			from mercurial.repo import RepoError
		del self
		globals().update(vars())

	def is_valid(self):
		return 'hg' in globals() and self.version_match()

	def version_match(self):
		return version not in self.OLD_VERSIONS

	def _get_repo(self):
		return hg.repository(ui.ui(), path=self.location)

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
		match = cmdutil.match(self.repo, [], {}, default='relglob')
		match.bad = lambda x, y: False
		return (abs
			for abs in self.repo[rev].walk(match)
			if (rev or abs in self.repo.dirstate)
			and abs not in excluded
			)

class LegacyLibraryManager(LibraryManager):
	def version_match(self):
		return version in self.OLD_VERSIONS

	def find_files(self):
		excluded = self._get_excluded()
		from mercurial import util
		node = None
		walker = cmdutil.walk(self.repo, [], {}, node=node,
			badmatch=util.always, default='relglob')
		return (abs
			for src, abs, rel, exact in walker
			if src != 'b' and (node or abs in repo.dirstate)
			and abs not in excluded
			)

def hg_file_finder(dirname="."):
	"""
	Find the files in ``dirname`` under Mercurial version control
	according to the setuptools spec (see
	http://peak.telecommunity.com/DevCenter/setuptools#adding-support-for-other-revision-control-systems
	).
	"""
	import distutils.log
	dirname = dirname or '.'
	for mgr in HGRepoManager.get_valid_managers(dirname):
		try:
			return mgr.find_files()
		except BaseException, e:
			distutils.log.warn("Error in %s: %s", mgr, e)
	return []
