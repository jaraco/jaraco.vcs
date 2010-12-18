from setuptools import setup, find_packages
long_description = open('README').read()

# HGTools uses a special technique for getting the version from
#  mercurial, because it can't require itself to install itself.
# Don't use this technique in your project. Instead, follow the
#  directions in the README or see jaraco.util for an example.
from hgtools.plugins import calculate_version, patch_egg_info
patch_egg_info(force_hg_version=True)

setup(
    name="hgtools",
    version=calculate_version(),
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
            "use_hg_version_increment = hgtools.plugins:version_calc",
        ],
    },
)
