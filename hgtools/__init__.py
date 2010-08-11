"""
Classes for working with repositories using the Mercurial version
control system. Includes a plugin for setuptools to find files managed
by the version control system.

Classes support using the native Python library interfaces or using the
hg(1) command as a subprocess.
"""
__version__ = '0.4'
__author__ = 'Jannis Leidel/Jason R. Coombs'
__all__ = ['file_finder_plugin', 'get_manager', 'HGRepoManager']

import os
import subprocess
try:
	from collections import namedtuple
except ImportError:
	# Python 2.5 compat
	from hgtools.namedtuple_backport import namedtuple
from distutils.version import StrictVersion
import operator

def find(pred, items):
	"""
	Find the index of the first element in items for which pred returns
	True
	>>> find(lambda x: x > 3, range(100))
	4
	>>> find(lambda x: x < -3, range(100)) is None
	True
	"""
	for i, item in enumerate(items):
		if pred(item): return i

def rfind(pred, items):
	"""
	Find the index of the last element in items for which pred returns
	True. Returns a negative number useful for indexing from the end
	of a list or tuple.
	
	>>> rfind(lambda x: x > 3, [5,4,3,2,1])
	-4
	"""
	return -find(pred, reversed(items))-1

class SummableVersion(StrictVersion):
	"""
	A special version of a StrictVersion which can be added to another
	StrictVersion.
	
	>>> SummableVersion('1.1') + StrictVersion('2.3')
	SummableVersion ('3.4')
	"""
	def __add__(self, other):
		result = SummableVersion(str(self))
		result.version = tuple(map(operator.add, self.version, other.version))
		return result

	def reset_less_significant(self, significant_version):
		"""
		Reset to zero all version info less significant than the
		indicated version.
		>>> ver = SummableVersion('3.1.2')
		>>> ver.reset_less_significant(SummableVersion('0.1'))
		>>> str(ver)
		'3.1'
		"""
		nonzero = lambda x: x != 0
		version_len = 3 # strict versions are always a tuple of 3
		significant_pos = rfind(nonzero, significant_version.version)
		significant_pos = version_len + significant_pos + 1
		self.version = (self.version[:significant_pos]
			+ (0,)*(version_len - significant_pos) )

	def as_number(self):
		"""
		>>> str(SummableVersion('1.9.3').as_number())
		'1.93'
		"""
		def combine(subver, ver):
			return subver/10.0 + ver
		return reduce(combine, reversed(self.version))

class VersionManagement(object):
	"""
	Version functions for HGRepoManager classes
	"""
	
	increment = '0.0.1'

	def get_strict_versions(self):
		"""
		Return all version tags that can be represented by a
		StrictVersion.
		"""
		for tag in self.get_tags():
			try:
				yield StrictVersion(tag.tag)
			except ValueError:
				pass

	def get_tagged_version(self):
		"""
		Get the version of the local repository as a StrictVersion or
		None if no viable tag exists.
		"""
		try:
			# use 'xxx' because StrictVersion(None) is apparently ok
			return StrictVersion(self.get_tag() or 'xxx')
		except ValueError:
			pass

	def get_latest_version(self):
		"""
		Determine the latest version ever released of the project in
		the repo (based on tags).
		"""
		versions = sorted(self.get_strict_versions(), reverse=True)
		next = lambda i: i.next()
		return next(iter(versions))

	def get_current_version(self, increment=None):
		"""
		Return as a string the version of the current state of the
		repository -- a tagged version, if present, or the next version
		based on prior tagged releases.
		"""
		ver = self.get_tagged_version() or str(self.get_next_version(increment))+'dev'
		return str(ver)

	def get_next_version(self, increment=None):
		"""
		Return the next version based on prior tagged releases.
		"""
		increment = increment or self.increment
		return self.infer_next_version(self.get_latest_version(), increment)

	@staticmethod
	def infer_next_version(last_version, increment):
		"""
		Given a simple application version (as a StrictVersion),
		and an increment (1.0, 0.1, or 0.0.1), guess the next version.
		
		# set up a shorthand for examples
		>>> VM_infer = lambda *params: str(VersionManagement.infer_next_version(*params))
		
		>>> VM_infer('3.2', '0.0.1')
		'3.2.1'
		>>> VM_infer(StrictVersion('3.2'), '0.0.1')
		'3.2.1'
		>>> VM_infer('3.2.3', '0.1')
		'3.3'
		>>> VM_infer('3.1.2', '1.0')
		'4.0'
		
		Subversions never increment parent versions
		>>> VM_infer('3.0.9', '0.0.1')
		'3.0.10'
		
		If it's a prerelease version, just remove the prerelease.
		>>> VM_infer('3.1a1', '0.0.1')
		'3.1'
		"""
		last_version = SummableVersion(str(last_version))
		if last_version.prerelease:
			last_version.prerelease = None
			return str(last_version)
		increment = SummableVersion(increment)
		sum = last_version + increment
		sum.reset_less_significant(increment)
		return sum


class HGRepoManager(VersionManagement, object):
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
		classes = (LibraryManager, LegacyLibraryManager, SubprocessManager)
		force_cmd = os.environ.get('HGTOOLS_FORCE_CMD', False)
		if force_cmd:
			classes = (SubprocessManager, LibraryManager, LegacyLibraryManager)
		managers = (cls(location) for cls in classes)
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
			cwd=self.location)
		stdout, stderr = proc.communicate()
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
		return self._run_cmd([self.exe, 'identify', '-t']).strip() or None

	def get_tags(self):
		tagged_revision = namedtuple('tagged_revision', 'tag revision')
		lines = self._run_cmd([self.exe, 'tags']).splitlines()
		return (tagged_revision(*line.split()) for line in lines if line)			

class LibraryManager(HGRepoManager):
	"""
	An HGRepoManager implemented by exercising the mercurial Python APIs
	directly.
	"""
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

def file_finder_plugin(dirname="."):
	"""
	Find the files in ``dirname`` under Mercurial version control
	according to the setuptools spec (see
	http://peak.telecommunity.com/DevCenter/setuptools#adding-support-for-other-revision-control-systems
	).
	"""
	import distutils.log
	dirname = dirname or '.'
	try:
		for mgr in HGRepoManager.get_valid_managers(dirname):
			try:
				return mgr.find_files()
			except BaseException, e:
				distutils.log.warn("Error in hgtools.%s: %s", mgr, e)
	except BaseException, e:
		distutils.log.warn("Error getting managers in hgtools.file_finder_plugin: %s", e)
	return []

def patch_egg_info(force_hg_version=False):
	from setuptools.command.egg_info import egg_info
	from pkg_resources import safe_version
	import functools
	orig_ver = egg_info.tagged_version
	@functools.wraps(orig_ver)
	def tagged_version(self):
		using_hg_version = (
			force_hg_version
			or self.distribution.use_hg_version
			or self.distribution.use_hg_version_increment
			)
		if using_hg_version:
			result = safe_version(self.distribution.get_version())
		else:
			result = orig_ver(self)
		self.tag_build = result
		return result
	egg_info.tagged_version = tagged_version

def calculate_version(default_increment=None):
	# The version is cached in the tag_build value in setup.cfg (so that
	#  sdist versions will have a copy of the version as determined at
	#  the build environment).
	from ConfigParser import ConfigParser
	parser = ConfigParser()
	parser.read('setup.cfg')
	has_tag_build = (parser.has_section('egg_info')
		and 'tag_build' in parser.options('egg_info'))
	if has_tag_build:
		# a cached version is available, so use it.
		version = parser.get('egg_info', 'tag_build')
	else:
		# We don't have a version stored in tag_build, so calculate
		#  the version using an HGRepoManager.
		# for now, force the CMD version, because the library version
		#  is not implemented.
		os.environ['HGTOOLS_FORCE_CMD'] = 'True'
		mgr = HGRepoManager.get_first_valid_manager()
		version = mgr.get_current_version(default_increment)
	return version

def version_calc_plugin(dist, attr, value):
	"""
	Handler for parameter to setup(use_hg_version=value)
	"""
	if not value: return
	# if the user indicates an increment, use it
	increment = value if 'increment' in attr else None
	dist.metadata.version = calculate_version(increment)
	patch_egg_info()


# kept for backward-compatibility
get_manager = HGRepoManager.get_first_valid_manager
