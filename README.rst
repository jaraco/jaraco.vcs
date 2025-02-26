.. image:: https://img.shields.io/pypi/v/jaraco.vcs.svg
   :target: https://pypi.org/project/jaraco.vcs

.. image:: https://img.shields.io/pypi/pyversions/jaraco.vcs.svg

.. image:: https://github.com/jaraco/jaraco.vcs/actions/workflows/main.yml/badge.svg
   :target: https://github.com/jaraco/jaraco.vcs/actions?query=workflow%3A%22tests%22
   :alt: tests

.. image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v2.json
    :target: https://github.com/astral-sh/ruff
    :alt: Ruff

.. .. image:: https://readthedocs.org/projects/PROJECT_RTD/badge/?version=latest
..    :target: https://PROJECT_RTD.readthedocs.io/en/latest/?badge=latest

.. image:: https://img.shields.io/badge/skeleton-2025-informational
   :target: https://blog.jaraco.com/skeleton

Usage
=====

jaraco.vcs
provides classes for inspecting and working with repositories in the
Mercurial and Git version control systems (VCS).

The classes provided are designed to use subprocess invocation to
leverage the command-line interfaces of the VCS tools ``hg`` and ``git``. An
in-process Repo for Mercurial exists but has been disabled due to
issues that arise when run in certain environments (namely setuptools
sandboxing).

Auto Version Numbering
----------------------

This project adds support for automatically generating
project version numbers from a source code repository under
development.

To use this feature, the project must follow the following assumptions:

- Repo tags are used to indicate released versions.
- Tag names are specified as the version only (i.e. 0.1 or v0.1 and
  not release-0.1)
- Released versions currently must conform to the Version in
  `packaging <https://pypi.org/project/packaging>`_. Any tags
  that don't match this scheme will be ignored.

Thereafter, use the Repo.get_current_version to
determine the version of the local code. If the current revision is tagged
with a valid version, that version will be used. Otherwise, the tags in
the repo will be searched, the latest release will be found, and the
function will infer the upcoming release version.

For example, if the repo contains the tags 0.1, 0.2, and 0.3 and the
repo is not on any of those tags, get_current_version will return
'0.3.1dev' and get_current_version(increment='0.1') will return
'0.4dev'.

Example::

    >>> import jaraco.vcs
    >>> jaraco.vcs.repo().get_current_version()
    '9.0.1.dev0'
