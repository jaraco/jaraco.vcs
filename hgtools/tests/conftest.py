import os

import pytest

from hgtools import managers

@pytest.fixture
def hg_repo(tmpdir):
	tmpdir.chdir()
	mgr = managers.MercurialManager()
	mgr._invoke('init', '.')
	os.makedirs('bar')
	touch('bar/baz')
	mgr._invoke('addremove')
	mgr._invoke('ci', '-m', 'committed')
	with open('bar/baz', 'w') as baz:
		baz.write('content')
	mgr._invoke('ci', '-m', 'added content')
	return tmpdir


def touch(filename):
	with open(filename, 'a'):
		pass
