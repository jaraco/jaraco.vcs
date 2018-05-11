import os

import pytest

from hgtools import managers
from hgtools.managers import cmd
from hgtools.managers import subprocess


def test_subprocess_manager_invalid_when_exe_missing():
	"""
	If the hg executable dosen't exist, the manager should report
	False for .is_valid().
	"""
	non_existent_exe = '/non_existent_executable'
	assert not os.path.exists(non_existent_exe)
	mgr = subprocess.GitManager()
	mgr.exe = non_existent_exe
	assert not mgr.is_valid()


@pytest.mark.usefixtures("git_repo", scope='function')
class TestTags:
	def setup_method(self, method):
		self.mgr = managers.GitManager('.')

	def teardown_method(self, method):
		del self.mgr

	def test_single_tag(self):
		assert self.mgr.get_tags() == set([])
		self.mgr._invoke('tag', '-am', "Tagging 1.0", '1.0')
		assert self.mgr.get_tags() == set(['1.0'])
		self.mgr._invoke('checkout', '1.0')
		assert self.mgr.get_tags() == set(['1.0'])


class TestParseVersion:
	def test_simple(self):
		assert cmd.Git._parse_version('git version 1.9.3') == '1.9.3'

	def test_trailing_mess(self):
		val = cmd.Git._parse_version('git version 1.9.3 (Mac OS X)')
		assert val == '1.9.3'
