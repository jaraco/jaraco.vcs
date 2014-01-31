import os

import pytest

from hgtools import managers
from hgtools.managers import subprocess

def test_subprocess_manager_invalid_when_exe_missing():
	"""
	If the hg executable dosen't exist, the manager should report
	False for .is_valid().
	"""
	non_existent_exe = '/non_existent_executable'
	assert not os.path.exists(non_existent_exe)
	mgr = subprocess.MercurialManager()
	mgr.exe = non_existent_exe
	assert not mgr.is_valid()

@pytest.mark.usefixtures("hg_repo", scope='function')
class TestRelativePaths(object):
	"""
	Issue #9 demonstrated that the Manager would inadvertently return too many
	files when location is not the root of the repo. This test demonstrates
	the expected behavior.
	"""
	def test_nested_child(self):
		test_mgr = managers.MercurialManager('.')
		assert test_mgr.find_files() == [os.path.join('bar', 'baz')]

	def test_manager_in_child(self):
		test_mgr = managers.MercurialManager('bar')
		assert test_mgr.find_files() == ['baz']

	def test_current_dir_in_child(self):
		os.chdir('bar')
		test_mgr = managers.MercurialManager('.')
		assert test_mgr.find_files() == ['baz']

@pytest.mark.usefixtures("hg_repo", scope='function')
class TestTags(object):
	def setup_method(self, method):
		self.mgr = managers.MercurialManager('.')

	def teardown_method(self, method):
		del self.mgr

	def test_single_tag(self):
		self.mgr._invoke('tag', '1.0')
		assert self.mgr.get_tags() == set(['tip'])
		self.mgr._invoke('update', '1.0')
		assert self.mgr.get_tags() == set(['1.0'])

	def test_no_tags(self):
		"No tag should return empty set"
		assert self.mgr.get_tags('0') == set([])

	def test_local_modifications(self):
		"Local modifications should return empty set"
		with open('bar/baz', 'w') as f:
			f.write('changed')
		assert self.mgr.get_tags() == set([])

	def test_parent_tag(self):
		self.mgr._invoke('tag', '1.0')
		assert self.mgr.get_tags() == set(['tip'])
		assert self.mgr.get_parent_tags() == set(['tip'])
		assert self.mgr.get_parent_tags('.') == set(['1.0'])
		assert self.mgr.get_parent_tags('tip') == set(['1.0'])
		self.mgr._invoke('tag', '1.1')
		assert self.mgr.get_tags() == set(['tip'])
		assert self.mgr.get_parent_tags() == set(['tip'])
		assert self.mgr.get_parent_tags('.') == set(['1.1'])
		assert self.mgr.get_parent_tags('tip') == set(['1.1'])

	def test_two_tags_same_revision(self):
		"""
		Always return the latest tag for a given revision
		"""
		self.mgr._invoke('tag', '1.0')
		self.mgr._invoke('tag', '-r', '1.0', '1.1')
		self.mgr._invoke('update', '1.0')
		assert set(self.mgr.get_tags()) == set(['1.0', '1.1'])

	def test_two_tags_same_revision_lexicographically_earlier(self):
		"""
		Always return the latest tag for a given revision
		"""
		self.mgr._invoke('tag', '1.9')
		self.mgr._invoke('tag', '-r', '1.9', '1.10')
		self.mgr._invoke('update', '1.9')
		assert set(self.mgr.get_tags()) == set(['1.9', '1.10'])
