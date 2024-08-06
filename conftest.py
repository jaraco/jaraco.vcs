import pytest

import jaraco.path


@pytest.fixture(autouse=True)
def _isolate_home(tmp_home_dir):
    """Isolate the tests from a developer's VCS config."""


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
def hg_repo(hg_repo):
    repo = hg_repo
    jaraco.path.build(rev1)
    repo._invoke('addremove')
    repo._invoke('ci', '-m', 'committed')
    jaraco.path.build(rev2)
    repo._invoke('ci', '-m', 'added content')
    return repo


@pytest.fixture
def git_repo(git_repo):
    repo = git_repo
    jaraco.path.build(rev1)
    repo._invoke('add', '.')
    repo._invoke('commit', '-m', 'committed')
    jaraco.path.build(rev2)
    repo._invoke('commit', '-am', 'added content')
    return repo
