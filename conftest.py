import pathlib

import pytest

import jaraco.path
from jaraco import vcs


# isolate the tests from a developer's VCS config
pytestmark = pytest.mark.usefixtures('tmp_home_dir')


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
    repo = vcs.Mercurial()
    _ensure_present(repo)
    repo._invoke('init', '.')
    jaraco.path.build(source_tree)
    repo._invoke('addremove')
    repo._invoke('ci', '-m', 'committed')
    pathlib.Path('bar/baz').write_text('content', encoding='utf-8')
    repo._invoke('ci', '-m', 'added content')
    return repo


@pytest.fixture
def git_repo(temp_work_dir):
    repo = vcs.Git()
    _ensure_present(repo)
    repo._invoke('init')
    repo._invoke('config', 'user.email', 'vip@example.com')
    repo._invoke('config', 'user.name', 'Important User')
    jaraco.path.build(source_tree)
    repo._invoke('add', '.')
    repo._invoke('commit', '-m', 'committed')
    pathlib.Path('bar/baz').write_text('content', encoding='utf-8')
    repo._invoke('commit', '-am', 'added content')
    return repo
