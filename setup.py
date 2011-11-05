# -*- coding: UTF-8 -*-

"""
Setup script for building hgtools distribution

Copyright © 2010-2011 Jason R. Coombs
"""

from setuptools import find_packages
long_description = open('README').read()

# HGTools uses a special technique for getting the version from
#  mercurial, because it can't require itself to install itself.
# Don't use this technique in your project. Instead, follow the
#  directions in the README or see jaraco.util for an example.
from hgtools.plugins import calculate_version, patch_egg_info
patch_egg_info(force_hg_version=True)

# set up distutils/setuptools to convert to Python 3 when
#  appropriate
try:
    from distutils.command.build_py import build_py_2to3 as build_py
    # exclude some fixers that break already compatible code
    from lib2to3.refactor import get_fixers_from_package
    fixers = get_fixers_from_package('lib2to3.fixes')
    for skip_fixer in []:
        fixers.remove('lib2to3.fixes.fix_' + skip_fixer)
    build_py.fixer_names = fixers
except ImportError:
    from distutils.command.build_py import build_py

setup_params = dict(
    name="hgtools",
    version=calculate_version(options=dict(increment='0.0.1')),
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
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Topic :: Software Development :: Version Control",
        "Framework :: Setuptools Plugin",
    ],
    packages=find_packages(),
    entry_points = {
        "setuptools.file_finders": [
            "hg = hgtools.plugins:file_finder"
        ],
        "distutils.setup_keywords": [
            "use_hg_version = hgtools.plugins:version_calc",
        ],
    },
    cmdclass=dict(build_py=build_py),
)

if __name__ == '__main__':
	from setuptools import setup
	setup(**setup_params)
