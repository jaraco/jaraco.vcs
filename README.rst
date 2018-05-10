.. image:: https://img.shields.io/pypi/v/hgtools.svg
   :target: https://pypi.org/project/hgtools

.. image:: https://img.shields.io/pypi/pyversions/hgtools.svg

.. image:: https://img.shields.io/pypi/dm/hgtools.svg

.. .. image:: https://img.shields.io/appveyor/ci/jaraco/skeleton/master.svg
..    :target: https://ci.appveyor.com/project/jaraco/skeleton/branch/master

.. image:: https://img.shields.io/travis/jaraco/hgtools/master.svg
   :target: https://travis-ci.org/jaraco/hgtools

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
