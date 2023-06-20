from unittest import mock
import pytest

from jaraco import vcs


def test_existing_only():
    """
    Test the static method RepoManager.existing_only.
    """
    # presumably, '/' is never an hg repo - at least for our purposes, that's
    #  a reasonable assumption.
    mgrs = vcs.RepoManager.get_valid_managers('/')
    existing = list(vcs.RepoManager.existing_only(mgrs))
    assert not existing


@mock.patch.object(
    vcs.RepoManager,
    'get_valid_managers',
    classmethod(lambda cls, location: iter(())),
)
def test_no_valid_managers():
    """
    When no valid managers can be found, a StopIteration is raised providing
    a nice message.
    """
    with pytest.raises(StopIteration) as err:
        vcs.RepoManager.get_first_valid_manager()
    assert 'no source repo' in str(err).lower()
