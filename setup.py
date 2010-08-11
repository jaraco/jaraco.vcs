from setuptools import setup, find_packages
long_description = open('README.txt').read()

from hgtools import calculate_version, patch_egg_info
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
        "Development Status :: 4 - Beta",
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
            "hg = hgtools:file_finder_plugin"
        ],
        "distutils.setup_keywords": [
            "use_hg_version = hgtools:version_calc_plugin",
            "use_hg_version_increment = hgtools:version_calc_plugin",
        ],
    },
)
