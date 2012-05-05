"""
hgtools implements several repo managers, each of which provides an interface
to Mercurial functionality.
"""

from __future__ import with_statement

import os
import posixpath
import subprocess
import re
import itertools
import operator

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
		"Return True if this is a valid manager for this location."
		return True

	def setup(self):
		pass

	@staticmethod
	def get_valid_managers(location):
		"""
		Get the valid HGRepoManagers for this location.
		"""
		force_cmd = os.environ.get('HGTOOLS_FORCE_CMD', False)
		class_order = (
			(SubprocessManager, LibraryManager)
			if force_cmd else
			(LibraryManager, SubprocessManager)
			)
		managers = (cls(location) for cls in class_order)
		return (mgr for mgr in managers if mgr.is_valid())

	@staticmethod
	def get_first_valid_manager(location='.'):
		return next(HGRepoManager.get_valid_managers(location))

	@staticmethod
	def existing_only(managers):
		"""
		Return only those managers that refer to an existing repo
		"""
		return (mgr for mgr in managers if mgr.find_root())

	def __repr__(self):
		class_name = self.__class__.__name__
		loc = self.location
		return '%(class_name)s(%(loc)r)' % vars()

	def find_root(self):
		raise NotImplementedError()

	def find_files(self):
		raise NotImplementedError()

	def get_tag(self):
		raise NotImplementedError()

	def get_tags(self):
		raise NotImplementedError()

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

class SubprocessManager(HGRepoManager):
	"""
	An HGRepoManager implemented by calling into the 'hg' command-line
	as a subprocess.
	"""
	exe = 'hg'

	def is_valid(self):
		try:
			self._run_cmd([self.exe, 'version'])
		except Exception:
			return False
		return super(SubprocessManager, self).is_valid()

	@staticmethod
	def _safe_env():
		"""
		Return an environment safe for calling an `hg` subprocess.

		Removes MACOSX_DEPLOYMENT_TARGET from the env, as if there's a
		mismatch between the local Python environment and the environment
		in which `hg` is installed, it will cause an exception. See
		https://bitbucket.org/jaraco/hgtools/issue/7 for details.
		"""
		env = os.environ.copy()
		env.pop('MACOSX_DEPLOYMENT_TARGET', None)
		return env

	def _run_cmd(self, cmd):
		proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
			stderr=subprocess.PIPE, cwd=self.location, env=self._safe_env())
		stdout, stderr = proc.communicate()
		if not proc.returncode == 0:
			raise RuntimeError(stderr.strip() or stdout.strip())
		return stdout.decode('utf-8')

	def find_root(self):
		try:
			return self._run_cmd([self.exe, 'root']).strip()
		except Exception:
			pass

	def find_files(self):
		"""
		Find versioned files in self.location
		"""
		cmd = [self.exe, 'locate', '-I', '.']
		all_files = self._run_cmd(cmd).splitlines()
		# now we have a list of all files in self.location relative to
		#  self.find_root()
		# Remove the parent dirs from them.
		from_root = os.path.relpath(self.location, self.find_root())
		loc_rel_paths = [os.path.relpath(path, from_root)
			for path in all_files]
		return loc_rel_paths

	def get_parent_tag(self, rev=None):
		cmd = [self.exe, 'parents']
		if rev:
			cmd.extend(['--rev', str(rev)])
		out = self._run_cmd(cmd)
		cs_pat = '^changeset:\s+(?P<local>\d+):(?P<hash>[0-9a-zA-Z]+)'
		matches = re.findall(cs_pat, out)
		if not len(matches) == 1:
			return
		_, parent_rev = matches.pop()
		return self.get_tag(parent_rev)

	def get_tag(self, rev=None):
		"""
		Get the most recent tag for the given revision specifier (or the
		current revision if not specified).
		"""
		rev_num = self._get_rev_num(rev)
		# rev_num might end with '+', indicating loca lmodifications.
		if rev_num.endswith('+'): return
		all_tags = self._read_tags_for_rev(rev_num)
		return all_tags[-1] if all_tags else None

	def _read_tags_for_rev(self, rev_num):
		"""
		Return the tags for revision sorted by when the tags were
		created (latest first)
		"""
		cmd = [self.exe, 'log', '-r', rev_num]
		res = self._run_cmd(cmd)
		tag_lines = [
			line for line in res.splitlines()
			if line.startswith('tag:')
		]
		header_pattern = re.compile('(?P<header>\w+?):\s+(?P<value>.*)')
		return [header_pattern.match(line).groupdict()['value']
			for line in tag_lines]

	def _get_rev_num(self, rev=None):
		"""
		Determine the revision number for a given revision specifier.
		"""
		# first, determine the numeric ID
		cmd = [self.exe, 'identify', '--num']
		# workaround for #4
		cmd.extend(['--config', 'defaults.identify='])
		if rev:
			cmd.extend(['--rev', rev])
		res = self._run_cmd(cmd)
		return res.strip()

	def _get_tags_by_num(self):
		"""
		Return a dictionary mapping revision number to tags for that number.
		"""
		by_revision = operator.attrgetter('revision')
		tags = sorted(self.get_tags(), key=by_revision)
		revision_tags = itertools.groupby(tags, key=by_revision)
		get_id = lambda rev: rev.split(':', 1)[0]
		return dict(
			(get_id(rev), [tr.tag for tr in tr_list])
			for rev, tr_list in revision_tags
		)

	def get_tags(self):
		tagged_revision = namedtuple('tagged_revision', 'tag revision')
		lines = self._run_cmd([self.exe, 'tags']).splitlines()
		return (
			tagged_revision(*line.rsplit(None, 1))
			for line in lines if line
		)

	def is_modified(self):
		out = self._run_cmd([self.exe, 'status', '-mard'])
		return bool(out)

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
			import mercurial.__version__
			import mercurial.hg
			import mercurial.ui
			import mercurial.cmdutil
			import mercurial.util
			import mercurial.error as repo_error
		except ImportError:
			pass

		try:
			# mercurial < 1.2
			import mercurial.repo as repo_error
		except ImportError:
			pass

		globals().update(vars())

	def is_valid(self):
		modules_present = 'mercurial' in globals() and self.version_match()
		return modules_present and super(LibraryManager, self).is_valid()

	def find_root(self):
		try:
			return self.repo.root
		except Exception:
			pass

	def version_match(self):
		return mercurial.__version__.version not in self.OLD_VERSIONS

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
