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

@contextlib.contextmanager
def replace_sysargv(params):
	sys_argv, sys.argv = sys.argv, params
	try:
		yield
	finally:
		sys.argv = sys.argv

class Result(object):
	pass

@contextlib.contextmanager
def capture_system_exit():
	res = Result()
	try:
		yield res
		res.code = 0
	except SystemExit as e:
		if isinstance(e.code, int):
			res.code = e.code
		else:
			res.code = 1
	except Exception:
		res.code = 1
		raise

class ProcessResult(object):
	pass

@contextlib.contextmanager
def in_process_context(params):
	res = ProcessResult()
	with capture_stdio() as stdio, replace_sysargv(params), capture_system_exit() as proc_res:
		yield res
	res.stdio = stdio
	res.returncode = proc_res.code

class LibraryManager(base.HGRepoManager):
	"""
	An HGRepoManager implemented by invoking the hg command in-process.
	"""
	exe = 'hg'

	def is_valid(self):
		modules_present = 'mercurial' in globals() and self.version_match()
		return modules_present and super(LibraryManager, self).is_valid()

	def _run_hg(self, *params):
		"""
		Run the hg command in-process with the supplied params.
		"""
		cmdline = [self.exe] + list(params)
		with in_process_context(cmdline) as result:
			mercurial.dispatch.run()
		stdout = result.stdio.stdout.getvalue()
		stderr = result.stdio.stderr.getvalue()
		if not result.returncode == 0:
			raise RuntimeError(stderr.strip() or stdout.strip())
		return stdout.decode('utf-8')

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
