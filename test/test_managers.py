import os
import contextlib
import tempfile
import shutil

from hgtools import managers

def test_subprocess_manager_invalid_when_exe_missing():
	"""
	If the hg executable dosen't exist, the manager should report
	False for .is_valid().
	"""
	non_existent_exe = '/non_existent_executable'
	assert not os.path.exists(non_existent_exe)
	mgr = managers.SubprocessManager()
	mgr.exe = non_existent_exe
	assert not mgr.is_valid()

def test_existing_only():
	"""
	Test the static method HGRepoManager.existing_only.
	"""
	# presumably, '/' is never an hg repo - at least for our purposes, that's
	#  a reasonable assumption.
	mgrs = managers.HGRepoManager.get_valid_managers('/')
	existing = list(managers.HGRepoManager.existing_only(mgrs))
	assert not existing

@contextlib.contextmanager
def tempdir_context():
	temp_dir = tempfile.mkdtemp()
	orig_dir = os.getcwd()
	try:
		os.chdir(temp_dir)
		yield temp_dir
	finally:
		os.chdir(orig_dir)
		shutil.rmtree(temp_dir)

@contextlib.contextmanager
def test_repo():
	with tempdir_context():
		mgr = managers.SubprocessManager()
		mgr._run_cmd([mgr.exe, 'init', 'foo'])
		os.chdir('foo')
		os.makedirs('bar')
		touch('bar/baz')
		mgr._run_cmd([mgr.exe, 'addremove'])
		mgr._run_cmd([mgr.exe, 'ci', '-m', 'committed'])
		yield


def touch(filename):
	with open(filename, 'a'):
		pass

class TestRelativePaths(object):
	"""
	Issue #9 demonstrated that we can inadvertently return too many
	files when location is not the root of the repo. This test demonstrates
	that we don't have that problem anymore.
	"""
	def test_nested_child(self):
		with test_repo():
			test_mgr = managers.SubprocessManager('.')
			assert test_mgr.find_files() == [os.path.join('bar', 'baz')]

	def test_manager_in_child(self):
		with test_repo():
			test_mgr = managers.SubprocessManager('bar')
			assert test_mgr.find_files() == ['baz']

	def test_current_dir_in_child(self):
		with test_repo():
			os.chdir('bar')
			test_mgr = managers.SubprocessManager('.')
			assert test_mgr.find_files() == ['baz']
