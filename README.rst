.. image:: https://img.shields.io/pypi/v/hgtools.svg
   :target: `PyPI link`_

.. image:: https://img.shields.io/pypi/pyversions/hgtools.svg
   :target: `PyPI link`_

.. _PyPI link: https://pypi.org/project/hgtools

.. image:: https://github.com/jaraco/hgtools/workflows/tests/badge.svg
   :target: https://github.com/jaraco/hgtools/actions?query=workflow%3A%22tests%22
   :alt: tests

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black
   :alt: Code style: Black

.. .. image:: https://readthedocs.org/projects/skeleton/badge/?version=latest
..    :target: https://skeleton.readthedocs.io/en/latest/?badge=latest

.. image:: https://img.shields.io/badge/skeleton-2021-informational
   :target: https://blog.jaraco.com/skeleton

Usage
=====

hgtools
provides classes for inspecting and working with repositories in the
Mercurial and Git version control systems (VCS).

The classes provided by hgtools are designed to use subprocess invocation to
leverage the command-line interfaces of the VCS tools ``hg`` and ``git``. An
in-process RepoManager for Mercurial exists but has been disabled due to
issues that arise when run in certain environments (namely setuptools
sandboxing).

Auto Version Numbering
**********************

With the 0.4 release, hgtools adds support for automatically generating
project version numbers from the repository in which the
project is developed.

To use this feature, your project must follow the following assumptions:

	 - Repo tags are used to indicate released versions.
	 - Tag names are specified as the version only (i.e. 0.1 and not
	   v0.1 or release-0.1)
	 - Released versions currently must conform to the StrictVersion in
	   distutils. Any tags that don't match this scheme will be ignored.
	   Future releases may relax this restriction.

Thereafter, you may use the RepoManager.get_current_version to
determine the version of your product. If the current revision is tagged
with a valid version, that version will be used. Otherwise, the tags in
the repo will be searched, the latest release will be found, and hgtools
will infer the upcoming release version.

For example, if the repo contains the tags 0.1, 0.2, and 0.3 and the
repo is not on any of those tags, get_current_version will return
'0.3.1dev' and get_current_version(increment='0.1') will return
'0.4dev'.
