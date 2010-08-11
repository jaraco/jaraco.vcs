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
determine the version of the product. If the current revision is tagged
with a valid version, that version will be used. Otherwise, the tags in
the repo will be searched, the latest release will be found, and hgtools
will infer the upcoming release version.

For example, if the repo contains the tags 0.1, 0.2, and 0.3 and the
repo is not on any of those tags, get_current_version will return
'0.3.1dev' and get_current_version(increment='0.1') will return
'0.4dev'.

A distutils hook has been created to hack setuptools to use this version
information automatically. To use this functionality, just use the
``use_hg_version`` or ``use_hg_version_increment`` parameters to setup.
For example::

    from setuptools import setup, find_packages
    setup(
        name="HelloWorld",
        use_hg_version=True,
        packages=find_packages(),
        setup_requires=["hgtools"],
    )

hgtools will use the mercurial version to determine the version of the
package (based on get_current_version). If an sdist is created, hgtools
will store the calculated version in the tag_build of the setup.cfg and
will use that version when deploying remotely.

See the jaraco.util setup.py for an example of this technique.

Options
*******

Set the ``HGTOOLS_FORCE_CMD`` environment variable before running
setup.py if you want to enforce the use of the hg command (though it
will then fall back to the native libraries if the command is not
available or fails to run).

Changes
*******

0.4.6
~~~~~
 * Fixed hgtools version tagging (again)

0.4.5
~~~~~
 * Restored calculated versioning for the hgtools project itself.

0.4.4
~~~~~
 * Fixed issue where use_hg_version_increment wasn't recognized.

0.4.3
~~~~~
 * Using a fixed version number for hgtools, because often hgtools isn't
   available when hgtools is being installed, resulting in versions like
   ``0.0.00.4.3``.

0.4.2
~~~~~
 * Fixed formatting errors in documentation.

0.4.1
~~~~~

 * Reformatted package layout so that other modules can be included.
 * Restored missing namedtuple_backport (provides Python 2.5 support).

0.4
~~~

 * First release supporting automatic versioning using mercurial tags.
