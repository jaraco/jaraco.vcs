from unittest import mock
import pytest

from hgtools import managers


def test_existing_only():
	"""
	Test the static method RepoManager.existing_only.
	"""
	# presumably, '/' is never an hg repo - at least for our purposes, that's
	#  a reasonable assumption.
	mgrs = managers.RepoManager.get_valid_managers('/')
	existing = list(managers.RepoManager.existing_only(mgrs))
	assert not existing


@mock.patch.object(
	managers.RepoManager, 'get_valid_managers',
	classmethod(lambda cls, location: iter(())))
def test_no_valid_managers():
	"""
	When no valid managers can be found, a StopIteration is raised providing
	a nice message.
	"""
	with pytest.raises(StopIteration) as err:
		managers.RepoManager.get_first_valid_manager()
	assert 'no source repo' in str(err).lower()
