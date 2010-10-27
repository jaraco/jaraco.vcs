"""
Classes for working with repositories using the Mercurial version
control system. Includes a plugin for setuptools to find files managed
by the version control system.

Classes support using the native Python library interfaces or using the
hg(1) command as a subprocess.
"""
__version__ = '0.6'
__author__ = 'Jannis Leidel/Jason R. Coombs'
__all__ = ['file_finder_plugin']

import os

from . import managers
from .py25compat import namedtuple

def file_finder_plugin(dirname="."):
	"""
	Find the files in ``dirname`` under Mercurial version control
	according to the setuptools spec (see
	http://peak.telecommunity.com/DevCenter/setuptools#adding-support-for-other-revision-control-systems
	).
	"""
	import distutils.log
	dirname = dirname or '.'
	try:
		for mgr in managers.HGRepoManager.get_valid_managers(dirname):
			try:
				return mgr.find_files()
			except Exception, e:
				distutils.log.warn("hgtools.%s could not find files: %s", mgr, e)
	except Exception, e:
		distutils.log.warn("Unexpected error finding valid managers in hgtools.file_finder_plugin: %s", e)
	return []

def patch_egg_info(force_hg_version=False):
	"""
	A hack to replace egg_info.tagged_version with a wrapped version
	that will use the mercurial version if indicated.
	"""
	from setuptools.command.egg_info import egg_info
	from pkg_resources import safe_version
	import functools
	orig_ver = egg_info.tagged_version
	@functools.wraps(orig_ver)
	def tagged_version(self):
		using_hg_version = (
			force_hg_version
			or getattr(self.distribution, 'use_hg_version', False)
			or getattr(self.distribution, 'use_hg_version_increment',
				False)
			)
		if using_hg_version:
			result = safe_version(self.distribution.get_version())
		else:
			result = orig_ver(self)
		self.tag_build = result
		return result
	egg_info.tagged_version = tagged_version

def calculate_version(default_increment=None):
	# The version is cached in the tag_build value in setup.cfg (so that
	#  sdist versions will have a copy of the version as determined at
	#  the build environment).
	from ConfigParser import ConfigParser
	parser = ConfigParser()
	parser.read('setup.cfg')
	has_tag_build = (parser.has_section('egg_info')
		and 'tag_build' in parser.options('egg_info'))
	if has_tag_build:
		# a cached version is available, so use it.
		version = parser.get('egg_info', 'tag_build')
	else:
		# We don't have a version stored in tag_build, so calculate
		#  the version using an HGRepoManager.
		# for now, force the CMD version, because the library version
		#  is not implemented.
		os.environ['HGTOOLS_FORCE_CMD'] = 'True'
		mgr = managers.HGRepoManager.get_first_valid_manager()
		version = mgr.get_current_version(default_increment)
	return version

def version_calc_plugin(dist, attr, value):
	"""
	Handler for parameter to setup(use_hg_version=value)
	"""
	if not value or not 'hg_version' in attr: return
	# if the user indicates an increment, use it
	increment = value if 'increment' in attr else None
	dist.metadata.version = calculate_version(increment)
	patch_egg_info()
