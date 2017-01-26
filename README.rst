.. image:: https://img.shields.io/pypi/v/hgtools.svg
   :target: https://pypi.org/project/hgtools

.. image:: https://img.shields.io/pypi/pyversions/hgtools.svg

.. image:: https://img.shields.io/pypi/dm/hgtools.svg

.. image:: https://img.shields.io/travis/jaraco/hgtools/master.svg
   :target: http://travis-ci.org/jaraco/hgtools

.. warning:: hgtools is defunct. It has been largely superseded by the
   `setuptools_scm <https://pypi.python.org/pypi/setuptools_scm>`_
   project.

License
=======

License is indicated in the project metadata (typically one or more
of the Trove classifiers). For more details, see `this explanation
<https://github.com/jaraco/skeleton/issues/1>`_.

Usage
=====

hgtools builds on the setuptools_hg plugin for setuptools. hgtools
provides classes for inspecting and working with repositories in the
Mercurial and Git version control systems (VCS).

hgtools provides a plugin for setuptools that enables setuptools to find
files managed by the VCS (currently only Mercurial support is implemented).

The classes provided by hgtools are designed to use subprocess invocation to
leverage the command-line interfaces of the VCS tools ``hg`` and ``git``. An
in-process RepoManager for Mercurial exists but has been disabled due to
issues that arise when run in certain environments (namely setuptools
sandboxing).

.. note:: The setuptools feature

  You can read about the setuptools plugin provided by hgtools in the
  `setuptools documentation`_. It basically returns a list of files that are
  under VCS when running the ``setup`` function, e.g. if
  you create a source and binary distribution. It's a simple yet effective way
  of not having to define package data (non-Python files) manually in MANIFEST
  templates (``MANIFEST.in``).

.. _setuptools documentation: http://pythonhosted.org/setuptools/setuptools.html#adding-support-for-other-revision-control-systems

Usage
*****

Here's a simple example of a setup.py that uses hgtools:

.. code-block:: python

    from setuptools import setup, find_packages
    setup(
        name="HelloWorld",
        version="0.1",
        packages=find_packages(),
        setup_requires=["hgtools"],
    )

If you run the setup.py above, setuptools will automatically download
hgtools to the directory where the setup.py is located at (and won't
install it anywhere else) to get all package data files from the
sourec code repository.

You should not need to, and I recommend you don't, install hgtools in
your site-packages directory. Let setuptools grab it on demand. Also,
try not to specify an upper bound for the requirement. Usually, simply
specifying 'hgtools' will get the latest version, which is likely to
remain compatible (as a plugin) for the life of the project. Specifying
an upper bound (i.e. `hgtools<1.1`) will only prevent you from getting
bug fixes. Only specify an upper bound if you require support for older
versions of Python.

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

A distutils hook has been created to hack setuptools to use this version
information automatically. To use this functionality, just use the
``use_vcs_version`` parameter to setup.
For example:

.. code-block:: python

    from setuptools import setup, find_packages
    setup(
        name="HelloWorld",
        use_vcs_version=True,
        packages=find_packages(),
        setup_requires=["hgtools"],
    )

If the value supplied to use_vcs_version resolves to True, hgtools will
use the tagged version to determine the version of the
package (based on get_current_version). If an sdist is created, hgtools
will store the calculated version in the tag_build of the setup.cfg and
will use that version when deploying remotely. Therefore, if you are
using auto-versioning, you should not use setuptools tags explicitly.

See the jaraco.util setup.py for an example of this technique.

Versioning Parameters
~~~~~~~~~~~~~~~~~~~~~

It's also possible to pass keyword parameters to use_vcs_version to
tweak how it generates version numbers. To pass parameters, instead of
setting `use_vcs_version = True`, set it to a non-empty dictionary with
one or more of the following parameters:

 - `increment`:
   A string indicating the default version increment for the project.
   By default, this value is '0.1', meaning hgtools will use the version
   '1.1dev' for builds following the 1.0 release and '1.10dev' for builds
   following a 1.9.3 release. Set this value to '1.0' or '0.0.1' for the
   current tree to help hgtools guess the target version.

 - `version_handler`:
   A Python function with the following signature:

   .. code-block:: python

       def calc_version(mgr, options):
           return str('1.0')

   hgtools will use this function instead of its default implementation
   to customize the version number calculation. The `mgr` object is the
   `hgtools.managers.base.RepoManager` object referencing the local repo
   and the `options` is the dictionary passed to use_vcs_version.

   Use this option, for example, to include the commit hash or local
   revision ID in the version:

   .. code-block:: python

       def id_as_version(mgr, options):
           "Always return the Mercurial revision ID as the version"
           id_n = mgr._invoke(['id', '-n']).strip()
           return id_n

       setup(
           #...
           use_vcs_version={'version_handler': id_as_version},
       )

   The first thing to note is the mgr does not yet provide a nice
   interface for getting anything but the tags for a revision, so the
   example digs into the underlying API to extract the ID. hgtools should
   provide better support in the HGRepoManager classes in future releases.

   Use this feature with caution. If you have not already read the
   `setuptools documentation on specifying a project version
   <http://packages.python.org/distribute/setuptools.html#specifying-your-project-s-version>`_,
   the author recommends you do read that.
