import os
import re
import operator
import itertools
import collections

import pkg_resources


TaggedRevision = collections.namedtuple('TaggedRevision', 'tag revision')


class Command(object):
	def is_valid(self):
		try:
			# Check if both command and repo are valid
			self._invoke('status')
		except Exception:
			return False
		return super(Command, self).is_valid()

	def version(self):
		"""
		Return the underlying version
		"""
		lines = iter(self._invoke('version').splitlines())
		version = next(lines).strip()
		return self._parse_version(version)

	@classmethod
	def _parse_version(cls, version):
		return re.search(cls.version_pattern, version).group(1)


class Mercurial(Command):
	exe = 'hg'
	version_pattern = r'Mercurial Distributed SCM \((.*?)\)'

	def find_root(self):
		try:
			return self._invoke('root').strip()
		except Exception:
			pass

	def find_files(self):
		"""
		Find versioned files in self.location
		"""
		all_files = self._invoke('locate', '-I', '.').splitlines()
		# now we have a list of all files in self.location relative to
		#  self.find_root()
		# Remove the parent dirs from them.
		from_root = os.path.relpath(self.location, self.find_root())
		loc_rel_paths = [
			os.path.relpath(path, from_root)
			for path in all_files]
		return loc_rel_paths

	def get_parent_revs(self, rev=None):
		cmd = [
			'parents', '--style', 'default',
			'--config', 'defaults.parents=']
		if rev:
			cmd.extend(['--rev', str(rev)])
		out = self._invoke(*cmd)
		cs_pat = r'^changeset:\s+(?P<local>\d+):(?P<hash>[0-9a-zA-Z]+)'
		return (
			match.groupdict()['local'] for match in
			re.finditer(cs_pat, out))

	def get_tags(self, rev=None):
		"""
		Get the tags for the given revision specifier (or the
		current revision if not specified).
		"""
		rev_num = self._get_rev_num(rev)
		# rev_num might end with '+', indicating local modifications.
		return (
			set(self._read_tags_for_rev(rev_num))
			if not rev_num.endswith('+')
			else set([])
		)

	def _read_tags_for_rev(self, rev_num):
		"""
		Return the tags for revision sorted by when the tags were
		created (latest first)
		"""
		return (tr.tag for tr in self._read_tags_for_revset(rev_num))

	def _read_tags_for_revset(self, spec):
		"""
		Return TaggedRevision for each tag/rev combination in the revset spec
		"""
		cmd = [
			'log', '--style', 'default', '--config', 'defaults.log=',
			'-r', spec]
		res = self._invoke(*cmd)
		header_pattern = re.compile(r'(?P<header>\w+?):\s+(?P<value>.*)')
		match_res = map(header_pattern.match, res.splitlines())
		matched_lines = filter(None, match_res)
		matches = (match.groupdict() for match in matched_lines)
		for match in matches:
			if match['header'] == 'changeset':
				id, sep, rev = match['value'].partition(':')
			if match['header'] == 'tag':
				tag = match['value']
				yield TaggedRevision(tag, rev)

	def _get_rev_num(self, rev=None):
		"""
		Determine the revision number for a given revision specifier.
		"""
		# first, determine the numeric ID
		cmd = ['identify', '--num']
		# workaround for #4
		cmd.extend(['--config', 'defaults.identify='])
		if rev:
			cmd.extend(['--rev', rev])
		res = self._invoke(*cmd)
		return res.strip()

	def _get_tags_by_num(self):
		"""
		Return a dictionary mapping revision number to tags for that number.
		"""
		by_revision = operator.attrgetter('revision')
		tags = sorted(self.get_tags(), key=by_revision)
		revision_tags = itertools.groupby(tags, key=by_revision)

		def get_id(rev):
			return rev.split(':', 1)[0]
		return dict(
			(get_id(rev), [tr.tag for tr in tr_list])
			for rev, tr_list in revision_tags
		)

	def get_repo_tags(self):
		lines = self._invoke('tags').splitlines()
		return (
			TaggedRevision(*line.rsplit(None, 1))
			for line in lines if line
		)

	def get_ancestral_tags(self, rev='.'):
		"""
		Like get_repo_tags, but only get those tags ancestral to the current
		changeset.
		"""
		spec = 'sort(ancestors({rev}), -date)'.format(**vars())
		return self._read_tags_for_revset(spec)

	def is_modified(self):
		out = self._invoke('status', '-mard')
		return bool(out)


class Git(Command):
	exe = 'git'
	version_pattern = r'git version (\d+\.\d+[^ ]*)'

	def is_valid(self):
		return super(Git, self).is_valid() and self.version_suitable()

	def version_suitable(self):
		req_ver = pkg_resources.parse_version('1.7.10')
		act_ver = pkg_resources.parse_version(self.version())
		return act_ver >= req_ver

	def find_root(self):
		try:
			return self._invoke('rev-parse', '--top-level').strip()
		except Exception:
			pass

	def find_files(self):
		all_files = self._invoke('ls-files').splitlines()
		return all_files

	def get_tags(self, rev=None):
		"""
		Return the tags for the current revision as a set
		"""
		rev = rev or 'HEAD'
		return set(self._invoke('tag', '--points-at', rev).splitlines())

	def get_repo_tags(self):
		cmd = [
			"for-each-ref", "--sort=-committerdate",
			"--format=%(refname:short) %(objectname:short)", "refs/tags"]

		lines = self._invoke(*cmd).splitlines()
		return (
			TaggedRevision(*line.rsplit(None, 1))
			for line in lines if line
		)

	def is_modified(self):
		"""
		Is the current state modified? (currently stubbed assuming no)
		"""
		return False
