from setuptools import setup

long_description = """
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

Here's an example of a setup.py that uses hgtools::

    from setuptools import setup, find_packages
    setup(
        name="HelloWorld",
        version="0.1",
        packages=find_packages(),
        setup_requires=["hgtools"],
    )

If you run the setup.py above, setuptools will automatically download setuptools_hg
to the directory where the setup.py is located at (and won't install it
anywhere else) to get all package data files from the Mercurial repository.

Options
*******

Set the ``HG_SETUPTOOLS_FORCE_CMD`` environment variable before running
setup.py if you want to enforce the use of the hg command (though it
will then fall back to the native libraries if the command is not
available or fails to run).
"""

setup(
    name="hgtools",
    version='0.3',
    author="Jannis Leidel/Jason R. Coombs",
    author_email="jaraco@jaraco.com",
    url="http://bitbucket.org/jaraco/hgtools/",
    download_url="http://bitbucket.org/jaraco/hgtools/downloads/",
    description="Classes and setuptools plugin for Mercurial repositories",
    long_description=long_description,
    license="GPL2",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Topic :: Software Development :: Version Control",
        "Framework :: Setuptools Plugin",
    ],
    py_modules=["hgtools"],
    entry_points = {
        "setuptools.file_finders": [
            "hg = hgtools:file_finder_plugin"
        ]
    }
)
