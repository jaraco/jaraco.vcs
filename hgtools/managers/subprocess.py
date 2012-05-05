from __future__ import absolute_import

import os
import re
import subprocess
import operator
import itertools

from hgtools.py25compat import namedtuple

from . import base

class SubprocessManager(base.HGRepoManager):
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
