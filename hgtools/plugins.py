"""
setuptools plugins
"""

import sys
try:
	# Prefer the Python 2 version of configparser because Python 3
	#  backport has issues when non-unicode strings are passed.
	# See issue #10 for details
	import ConfigParser as configparser
except ImportError:
	import configparser

from . import managers

__all__ = ['file_finder', 'version_calc']


def file_finder(dirname="."):
	"""
	Find the files in ``dirname`` under Mercurial version control
	according to the setuptools spec (see
	http://peak.telecommunity.com/DevCenter/setuptools#adding-support-for-other-revision-control-systems
	).
	"""
	import distutils.log
	dirname = dirname or '.'
	try:
		valid_mgrs = managers.RepoManager.get_valid_managers(dirname)
		valid_mgrs = managers.RepoManager.existing_only(valid_mgrs)
		for mgr in valid_mgrs:
			try:
				return mgr.find_all_files()
			except Exception:
				e = sys.exc_info()[1]
				distutils.log.warn(
					"hgtools.%s could not find files: %s",
					mgr, e)
	except Exception:
		e = sys.exc_info()[1]
		distutils.log.warn(
			"Unexpected error finding valid managers in "
			"hgtools.file_finder_plugin: %s", e)
	return []


def patch_egg_info(force_hg_version=False):
	"""
	A hack to replace egg_info.tagged_version with a wrapped version
	that will use the mercurial version if indicated.

	`force_hg_version` is used for hgtools itself.
	"""
	from setuptools.command.egg_info import egg_info
	from pkg_resources import safe_version
	import functools
	orig_ver = egg_info.tagged_version

	@functools.wraps(orig_ver)
	def tagged_version(self):
		vcs_param = (
			getattr(self.distribution, 'use_vcs_version', False)
			or getattr(self.distribution, 'use_hg_version', False)
		)
		using_hg_version = force_hg_version or vcs_param
		if force_hg_version:
			# disable patched `tagged_version` to avoid affecting
			#  subsequent installs in the same interpreter instance.
			egg_info.tagged_version = orig_ver
		if using_hg_version:
			result = safe_version(self.distribution.get_version())
		else:
			result = orig_ver(self)
		self.tag_build = result
		return result
	egg_info.tagged_version = tagged_version


def _calculate_version(mgr, options):
	default_increment = options.get('increment')
	repo_exists = bool(mgr.find_root())
	return (
		mgr.get_current_version(default_increment)
		if repo_exists else default_increment)


def calculate_version(options={}):
	# The version is cached in the tag_build value in setup.cfg (so that
	#  sdist packages will have a copy of the version as determined at
	#  the build environment).
	parser = configparser.ConfigParser()
	parser.read('setup.cfg')
	has_tag_build = (
		parser.has_section('egg_info')
		and 'tag_build' in parser.options('egg_info'))
	if has_tag_build:
		# a cached version is available, so use it.
		version = parser.get('egg_info', 'tag_build')
	else:
		# No version is stored in tag_build, so calculate
		#  the version using a RepoManager.
		mgr = managers.RepoManager.get_first_valid_manager()
		version_handler = options.get('version_handler', _calculate_version)
		try:
			version = version_handler(mgr, options)
		except Exception:
			version = options.get('increment')
	return version


def version_calc(dist, attr, value):
	"""
	Handler for parameter to setup(use_vcs_version=value)
	attr should be 'use_vcs_version' (also allows use_hg_version for
		compatibility).
	bool(value) should be true to invoke this plugin.
	value may optionally be a dict and supply options to the plugin.
	"""
	expected_attrs = 'use_hg_version', 'use_vcs_version'
	if not value or attr not in expected_attrs:
		return
	options = value if isinstance(value, dict) else {}
	dist.metadata.version = calculate_version(options)
	patch_egg_info()
