"""
hgtools implements several repo managers, each of which provides an interface
to Mercurial functionality.
"""

from __future__ import with_statement

import os
import posixpath
import itertools

from hgtools.py25compat import next
from hgtools import versioning
import hgtools

class HGRepoManager(versioning.VersionManagement, object):
	"""
	An abstract class defining some interfaces for working with
	Mercurial repositories.
	"""
	def __init__(self, location='.'):
		self.location = location
		self.setup()

	def is_valid(self):
		"Return True if this is a valid manager for this location."
		return True

	def setup(self):
		pass

	@staticmethod
	def get_valid_managers(location):
		"""
		Get the valid HGRepoManagers for this location.
		"""
		force_cmd = os.environ.get('HGTOOLS_FORCE_CMD', False)
		# until we have importlib, use __import__
		__import__('hgtools.managers.subprocess')
		__import__('hgtools.managers.library')
		class_order = (
			(
				hgtools.managers.subprocess.SubprocessManager,
				hgtools.managers.library.LibraryManager,
			)
			if force_cmd else
			(
				hgtools.managers.library.LibraryManager,
				hgtools.managers.subprocess.SubprocessManager,
			)
		)
		all_managers = (cls(location) for cls in class_order)
		return (mgr for mgr in all_managers if mgr.is_valid())

	@staticmethod
	def get_first_valid_manager(location='.'):
		return next(HGRepoManager.get_valid_managers(location))

	@staticmethod
	def existing_only(managers):
		"""
		Return only those managers that refer to an existing repo
		"""
		return (mgr for mgr in managers if mgr.find_root())

	def __repr__(self):
		class_name = self.__class__.__name__
		loc = self.location
		return '%(class_name)s(%(loc)r)' % vars()

	def find_root(self):
		raise NotImplementedError()

	def find_files(self):
		raise NotImplementedError()

	def get_tag(self):
		raise NotImplementedError()

	def get_tags(self):
		raise NotImplementedError()

	def is_modified(self):
		'Does the current working copy have modifications'
		raise NotImplementedError()

	def find_all_files(self):
		"""
		Find files including those in subrepositories.
		"""
		files = self.find_files()
		subrepo_files = (
			posixpath.join(subrepo.location, filename)
			for subrepo in self.subrepos()
			for filename in subrepo.find_files()
		)
		return itertools.chain(files, subrepo_files)

	def subrepos(self):
		try:
			with open(posixpath.join(self.location, '.hgsub')) as file:
				subs = list(file)
		except Exception:
			subs = []

		locs = [part.partition('=')[0].strip() for part in subs]
		return [self.__class__(posixpath.join(self.location, loc)) for loc in locs]
