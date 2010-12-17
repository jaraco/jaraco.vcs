import os
from hgtools.managers import SubprocessManager

def test_subprocess_manager_invalid_when_exe_missing():
	"""
	If the hg executable dosen't exist, the manager should report
	False for .is_valid().
	"""
	non_existent_exe = '/non_existent_executable'
	assert not os.path.exists(non_existent_exe)
	mgr = SubprocessManager()
	mgr.exe = non_existent_exe
	assert not mgr.is_valid()
