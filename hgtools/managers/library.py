from __future__ import absolute_import

import os
import sys
import io
import collections
import contextlib

from . import base

try:
	import mercurial.__version__
	import mercurial.dispatch
except ImportError:
	pass
except Exception:
	pass

SavedIO = collections.namedtuple('SavedIO', 'stdout stderr')

@contextlib.contextmanager
def capture_stdio():
	sys_stdout, sys.stdout = sys.stdout, io.BytesIO()
	sys_stderr, sys.stderr = sys.stderr, io.BytesIO()
	try:
		yield SavedIO(sys.stdout, sys.stderr)
	finally:
		sys.stdout = sys_stdout
		sys.stderr = sys.stderr

class LibraryManager(base.HGRepoManager):
	"""
	An HGRepoManager implemented by invoking the hg command in-process.
	"""

	def is_valid(self):
		modules_present = 'mercurial' in globals() and self.version_match()
		return modules_present and super(LibraryManager, self).is_valid()

	def _run_hg(self, *params):
		"""
		Run the hg command in-process with the supplied params.
		"""
		with capture_stdio() as captured:
			"""
			TODO:
			2) Catch SystemExit exceptions
			3) Set environment
			4) Invoke command
			5) Decode output
			"""

	def find_root(self):
		try:
			return self._run_hg('root')
		except Exception:
			pass

	def version_match(self):
		# TODO: what versions are supported?
		return mercurial.__version__.version >= '1.2'

	def find_files(self):
		"""
		Find versioned files in self.location
		"""
		all_files = self._run_hg('locate', '-I', '.').splitlines()
		# now we have a list of all files in self.location relative to
		#  self.find_root()
		# Remove the parent dirs from them.
		from_root = os.path.relpath(self.location, self.find_root())
		loc_rel_paths = [os.path.relpath(path, from_root)
			for path in all_files]
		return loc_rel_paths
