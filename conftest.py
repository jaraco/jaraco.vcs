import pytest

import jaraco.path
from jaraco import vcs


@pytest.fixture(autouse=True)
def _isolate_home(tmp_home_dir):
    """Isolate the tests from a developer's VCS config."""


def _ensure_present(repo):
    try:
        repo.version()
    except Exception:
        pytest.skip()


@pytest.fixture
def temp_work_dir(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    return tmp_path


rev1 = dict(
    bar=dict(
        baz="",
    ),
)


rev2 = dict(
    bar=dict(
        baz="content",
    ),
)


@pytest.fixture
def hg_repo(temp_work_dir):
    repo = vcs.Mercurial()
    _ensure_present(repo)
    repo._invoke('init', '.')
    jaraco.path.build(rev1)
    repo._invoke('addremove')
    repo._invoke('ci', '-m', 'committed')
    jaraco.path.build(rev2)
    repo._invoke('ci', '-m', 'added content')
    return repo


@pytest.fixture
def git_repo(temp_work_dir):
    repo = vcs.Git()
    _ensure_present(repo)
    repo._invoke('init')
    repo._invoke('config', 'user.email', 'vip@example.com')
    repo._invoke('config', 'user.name', 'Important User')
    jaraco.path.build(rev1)
    repo._invoke('add', '.')
    repo._invoke('commit', '-m', 'committed')
    jaraco.path.build(rev2)
    repo._invoke('commit', '-am', 'added content')
    return repo
