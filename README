hgtools
=======

hgtools builds on the setuptools_hg plugin for setuptools. hgtools
provides classes for inspecting and working with repositories in the
Mercurial version control system.

hgtools provides a plugin for setuptools that enables setuptools to find
files under the Mercurial version control system.

The classes provided by hgtools are designed to work natively with the
Mercurial Python libraries (in process) or fall back to using the
command-line program ``hg(1)`` if available. The command-line support is
especially useful inside virtualenvs
that don't have access to a system-wide installed Mercurial lib (i.e. when
the virtualenv was created with ``--no-site-packages``).

.. note:: The setuptools feature

  You can read about the setuptools plugin provided by hgtools in the
  `setuptools documentation`_. It basically returns a list of files that are
  under Mercurial version control when running the ``setup`` function, e.g. if
  you create a source and binary distribution. It's a simple yet effective way
  of not having to define package data (non-Python files) manually in MANIFEST
  templates (``MANIFEST.in``).

.. _setuptools documentation: http://peak.telecommunity.com/DevCenter/setuptools#adding-support-for-other-revision-control-systems

Usage
*****

Here's a simple example of a setup.py that uses hgtools::

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
Mercurial repository.

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
project version numbers from the mercurial repository in which the
project is developed.

To use this feature, your project must follow the following assumptions:

	 - Mercurial tags are used to indicate released versions.
	 - Tag names are specified as the version only (i.e. 0.1 and not
	   v0.1 or release-0.1)
	 - Released versions currently must conform to the StrictVersion in
	   distutils. Any tags that don't match this scheme will be ignored.
	   Future releases may relax this restriction.

Thereafter, you may use the HGToolsManager.get_current_version to
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
``use_hg_version`` parameter to setup.
For example::

    from setuptools import setup, find_packages
    setup(
        name="HelloWorld",
        use_hg_version=True,
        packages=find_packages(),
        setup_requires=["hgtools"],
    )

If the value supplied to use_hg_version resolves to True, hgtools will
use the mercurial version to determine the version of the
package (based on get_current_version). If an sdist is created, hgtools
will store the calculated version in the tag_build of the setup.cfg and
will use that version when deploying remotely. Therefore, if you are
using auto-versioning, you should not use setuptools tags explicitly.

See the jaraco.util setup.py for an example of this technique.

Versioning Parameters
~~~~~~~~~~~~~~~~~~~~~

It's also possible to pass keyword parameters to use_hg_version to
tweak how it generates version numbers. To pass parameters, instead of
setting `use_hg_version = True`, set it to a non-empty dictionary with
one or more of the following parameters:

 - `increment`:
   A string indicating the default version increment for the project.
   By default, this value is '0.1', meaning hgtools will use the version
   '1.1dev' for builds following the 1.0 release and '1.10dev' for builds
   following a 1.9.3 release. Set this value to '1.0' or '0.0.1' for the
   current tree to help hgtools guess the target version.

 - `version_handler`:
   A Python function with the following signature::

       def calc_version(mgr, options):
           return str('1.0')

   hgtools will use this function instead of its default implementation
   to customize the version number calculation. The `mgr` object is the
   `hgtools.managers.HGRepoManager` object referencing the local repo
   and the `options` is the dictionary passed to use_hg_version.

   Use this option, for example, to include the mercurial hash or local
   revision ID in the version::

       def id_as_version(mgr, options):
           "Always return the mercurial revision ID as the version"
           id_n = mgr._run_cmd([mgr.exe, 'id', '-n']).strip()
           return id_n

       setup(
           #...
           use_hg_version={'version_handler': id_as_version},
       )

   The first thing to note is the mgr does not yet provide a nice
   interface for getting anything but the tags for a revision, so the
   example digs into the underlying API to extract the ID. hgtools should
   provide better support in the HGRepoManager classes in future releases.

   Use this feature with caution. If you have not already read the
   `setuptools documentation on specifying a project version
   <http://packages.python.org/distribute/setuptools.html#specifying-your-project-s-version>`_,
   the author recommends you do read that.
