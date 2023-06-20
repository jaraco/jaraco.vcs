import pathlib

import pytest
import jaraco.path

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


bar_baz = dict(
    bar=dict(
        baz="",
    ),
)


@pytest.fixture
def hg_repo(tmpdir_as_cwd):
    mgr = managers.MercurialManager()
    _ensure_present(mgr)
    mgr._invoke('init', '.')
    jaraco.path.build(bar_baz)
    mgr._invoke('addremove')
    mgr._invoke('ci', '-m', 'committed')
    pathlib.Path('bar/baz').write_text('content', encoding='utf-8')
    mgr._invoke('ci', '-m', 'added content')
    return tmpdir_as_cwd


@pytest.fixture
def git_repo(tmpdir_as_cwd):
    mgr = managers.GitManager()
    _ensure_present(mgr)
    mgr._invoke('init')
    mgr._invoke('config', 'user.email', 'hgtools@example.com')
    mgr._invoke('config', 'user.name', 'HGTools')
    jaraco.path.build(bar_baz)
    mgr._invoke('add', '.')
    mgr._invoke('commit', '-m', 'committed')
    pathlib.Path('bar/baz').write_text('content', encoding='utf-8')
    mgr._invoke('commit', '-am', 'added content')
    return tmpdir_as_cwd
