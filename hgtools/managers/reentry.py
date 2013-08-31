from __future__ import absolute_import, with_statement

import sys
import io
import collections
import contextlib

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
	except BaseException:
		res.code = 1
		raise

class ProcessResult(object):
	pass

@contextlib.contextmanager
def in_process_context(params):
	res = ProcessResult()
	try:
		with capture_stdio() as stdio, replace_sysargv(params), capture_system_exit() as proc_res:
			yield res
	finally:
		res.stdio = stdio
		res.returncode = proc_res.code

