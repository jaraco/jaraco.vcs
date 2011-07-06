import os

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
