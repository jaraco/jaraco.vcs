# -*- coding: UTF-8 -*-

"""
Setup script for building hgtools distribution

Copyright © 2010-2011 Jason R. Coombs
"""

from __future__ import with_statement

import setuptools
import hgtools.plugins

with open('README') as readme:
	long_description = readme.read()

# HGTools uses a special technique for getting the version from
#  mercurial, because it can't require itself to install itself.
# Don't use this technique in your project. Instead, follow the
#  directions in the README or see jaraco.util for an example.

setup_params = dict(
	name="hgtools",
	version=hgtools.plugins.calculate_version(options=dict(increment='1.0')),
	author="Jannis Leidel/Jason R. Coombs",
	author_email="jaraco@jaraco.com",
	url="http://bitbucket.org/jaraco/hgtools/",
	download_url="http://bitbucket.org/jaraco/hgtools/downloads/",
	description="Classes and setuptools plugin for Mercurial repositories",
	long_description=long_description,
	license="GPL2",
	classifiers=[
		"Development Status :: 5 - Production/Stable",
		"Programming Language :: Python",
		"Programming Language :: Python :: 2.5",
		"Programming Language :: Python :: 2.6",
		"Programming Language :: Python :: 2.7",
		"Programming Language :: Python :: 3",
		"Intended Audience :: Developers",
		"Operating System :: OS Independent",
		"License :: OSI Approved :: GNU General Public License (GPL)",
		"Topic :: Software Development :: Version Control",
		"Framework :: Setuptools Plugin",
	],
	packages=setuptools.find_packages(),
	entry_points = {
		"setuptools.file_finders": [
			"hg = hgtools.plugins:file_finder"
		],
		"distutils.setup_keywords": [
			"use_hg_version = hgtools.plugins:version_calc",
		],
	},
	use_2to3=True,
)

if __name__ == '__main__':
	hgtools.plugins.patch_egg_info(force_hg_version=True)
	setuptools.setup(**setup_params)
