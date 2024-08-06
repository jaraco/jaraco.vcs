import pytest


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
    repo.commit_tree(rev1, 'committed')
    repo.commit_tree(rev2, 'added content')
    return repo


@pytest.fixture
def git_repo(git_repo):
    repo = git_repo
    repo.commit_tree(rev1, 'committed')
    repo.commit_tree(rev2, 'added content')
    return repo
