import pytest

from .. import vcs


def _ensure_present(repo):
    try:
        repo.version()
    except Exception:
        pytest.skip()


@pytest.fixture
def temp_work_dir(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    return tmp_path


@pytest.fixture
def hg_repo(temp_work_dir):
    repo = vcs.Mercurial()
    _ensure_present(repo)
    repo._invoke('init', '.')
    return repo


@pytest.fixture
def git_repo(temp_work_dir):
    repo = vcs.Git()
    _ensure_present(repo)
    repo._invoke('init')
    repo._invoke('config', 'user.email', 'vip@example.com')
    repo._invoke('config', 'user.name', 'Important User')
    return repo
