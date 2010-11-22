import os
import subprocess
from .py25compat import namedtuple, next
from . import versioning

class HGRepoManager(versioning.VersionManagement, object):
	"""
	An abstract class defining some interfaces for working with
	Mercurial repositories.
	"""
	def __init__(self, location='.'):
		self.location = location
		self.setup()

	def is_valid(self):
		return True

	def setup(self):
		pass

	@staticmethod
	def get_valid_managers(location):
		force_cmd = os.environ.get('HGTOOLS_FORCE_CMD', False)
		class_order = (
			(SubprocessManager, LibraryManager, LegacyLibraryManager)
			if force_cmd else
			(LibraryManager, LegacyLibraryManager, SubprocessManager)
			)
		managers = (cls(location) for cls in class_order)
		return (mgr for mgr in managers if mgr.is_valid())

	@staticmethod
	def get_first_valid_manager(location='.'):
		next = lambda i: i.next()
		return next(HGRepoManager.get_valid_managers(location))

	def __repr__(self):
		class_name = self.__class__.__name__
		loc = self.location
		return '%(class_name)s(%(loc)r)' % vars()

	def find_files(self):
		raise NotImplementedError()

	def get_tag(self):
		raise NotImplementedError()

	def get_tags(self):
		raise NotImplementedError()

class SubprocessManager(HGRepoManager):
	"""
	An HGRepoManager implemented by calling into the 'hg' command-line
	as a subprocess.
	"""
	exe = 'hg'

	def is_valid(self):
		return 0 == subprocess.call(
			[self.exe, 'version'],
			stdout=self._get_devnull(),
			)

	def _run_cmd(self, cmd):
		proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
			stderr=subprocess.PIPE,
			cwd=self.location)
		stdout, stderr = proc.communicate()
		if not proc.returncode == 0:
			raise RuntimeError(stderr.strip() or stdout.strip())
		return stdout

	def find_files(self):
		"""
		Find versioned files in self.location
		"""
		return self._run_cmd([self.exe, 'locate']).splitlines()

	@staticmethod
	def _get_devnull():
		return open(os.path.devnull, 'w')

	def get_tag(self):
		params = ['identify', '-t']
		# workaround for #4
		params.extend(['--config', 'defaults.identify='])
		return self._run_cmd([self.exe, *params]).strip() or None

	def get_tags(self):
		tagged_revision = namedtuple('tagged_revision', 'tag revision')
		lines = self._run_cmd([self.exe, 'tags']).splitlines()
		return (
			tagged_revision(*line.rsplit(None, 1))
			for line in lines if line
		)

class LibraryManager(HGRepoManager):
	"""
	An HGRepoManager implemented by exercising the mercurial Python APIs
	directly.
	"""
	OLD_VERSIONS = ('1.0', '1.0.1', '1.0.2')

	def setup(self):
		try:
			self._update_globals()
		except Exception:
			pass

	@staticmethod
	def _update_globals():
		try:
			from mercurial.__version__ import version
			from mercurial import hg, ui, cmdutil
			from mercurial.error import RepoError
		except ImportError:
			pass

		try:
			# mercurial < 1.2
			from mercurial.repo import RepoError
		except ImportError:
			pass

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
	"""
	A special subclass of LibraryManager which works with older versions
	of the Mercurial libraries.
	"""
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

