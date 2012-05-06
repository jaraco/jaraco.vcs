from distutils.version import StrictVersion

from hgtools import versioning

class VersionedObject(versioning.VersionManagement):
	def __init__(self, **kwargs):
		self.__dict__.update(kwargs)

class TestVersioning(object):
	def test_tag_versions(self):
		"""
		Versioning should only choose relevant tags (versions)
		"""
		mgr = VersionedObject(get_tags = lambda: tags)
		tags = set(['foo', 'bar', '3.0'])
		assert mgr.get_tagged_version() == StrictVersion('3.0')
		tags = set([])
		assert mgr.get_tagged_version() == None
		tags = set(['foo', 'bar'])
		assert mgr.get_tagged_version() == None

	def test_tag_priority(self):
		"""
		Since Mercurial provides tags in arbitrary order, the versioning
		support should infer the precedence (choose latest).
		"""
		mgr = VersionedObject(get_tags = lambda: tags)
		tags = set(['1.0', '1.1'])
		assert mgr.get_tagged_version() == '1.1'
		tags = set(['0.10', '0.9'])
		assert mgr.get_tagged_version() == '0.10'

	def test_defer_to_parent_tag(self):
		"""
		Use the parent tag if on the tip
		"""
		mgr = VersionedObject(
			get_tags = lambda rev=None: 'tip' if rev is None else set(['1.0']),
			get_parent_tags = lambda rev=None: '999'
		)
		assert mgr.get_tagged_version() == '1.0'
