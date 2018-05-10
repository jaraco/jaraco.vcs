import os

import pytest

from hgtools import managers


def _ensure_present(mgr):
	try:
		mgr.version()
	except Exception:
		pytest.skip()


@pytest.fixture
def tmpdir_as_cwd(tmpdir):
	with tmpdir.as_cwd():
		yield tmpdir


@pytest.fixture
def hg_repo(tmpdir_as_cwd):
	mgr = managers.MercurialManager()
	_ensure_present(mgr)
	mgr._invoke('init', '.')
	os.makedirs('bar')
	touch('bar/baz')
	mgr._invoke('addremove')
	mgr._invoke('ci', '-m', 'committed')
	with open('bar/baz', 'w') as baz:
		baz.write('content')
	mgr._invoke('ci', '-m', 'added content')
	return tmpdir_as_cwd


@pytest.fixture
def git_repo(tmpdir_as_cwd):
	mgr = managers.GitManager()
	_ensure_present(mgr)
	mgr._invoke('init')
	mgr._invoke('config', 'user.email', 'hgtools@example.com')
	mgr._invoke('config', 'user.name', 'HGTools')
	os.makedirs('bar')
	touch('bar/baz')
	mgr._invoke('add', '.')
	mgr._invoke('commit', '-m', 'committed')
	with open('bar/baz', 'w') as baz:
		baz.write('content')
	mgr._invoke('commit', '-am', 'added content')
	return tmpdir_as_cwd


def touch(filename):
	with open(filename, 'a'):
		pass
