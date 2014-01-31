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
