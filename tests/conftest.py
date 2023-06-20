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
def temp_work_dir(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    return tmp_path


source_tree = dict(
    bar=dict(
        baz="",
    ),
)


@pytest.fixture
def hg_repo(temp_work_dir):
    mgr = managers.MercurialManager()
    _ensure_present(mgr)
    mgr._invoke('init', '.')
    jaraco.path.build(source_tree)
    mgr._invoke('addremove')
    mgr._invoke('ci', '-m', 'committed')
    pathlib.Path('bar/baz').write_text('content', encoding='utf-8')
    mgr._invoke('ci', '-m', 'added content')


@pytest.fixture
def git_repo(temp_work_dir):
    mgr = managers.GitManager()
    _ensure_present(mgr)
    mgr._invoke('init')
    mgr._invoke('config', 'user.email', 'hgtools@example.com')
    mgr._invoke('config', 'user.name', 'HGTools')
    jaraco.path.build(source_tree)
    mgr._invoke('add', '.')
    mgr._invoke('commit', '-m', 'committed')
    pathlib.Path('bar/baz').write_text('content', encoding='utf-8')
    mgr._invoke('commit', '-am', 'added content')
