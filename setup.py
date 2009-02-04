from setuptools import setup

long_description = """
A plugin for setuptools to find files under Mercurial version control to be
automatically included as package data.

It works correctly with Mercurial 1.x and uses Mercurial's Python library by
default. It will however fall back to use the command line programm hg(1) to
determin the list of files.
"""

setup(
    name="setuptools_hg",
    version='0.1',
    author="Jannis Leidel",
    author_email="jannis@leidel.info",
    url="http://bitbucket.org/jezdez/setuptools_hg/",
    description="Setuptools plugin for finding files under Mercurial version control.",
    long_description=long_description,
    license="BSD License",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: BSD License",
        "Topic :: Software Development :: Version Control"
    ],
    py_modules=["setuptools_hg"],
    entry_points = {
        "setuptools.file_finders": [
            "hg = setuptools_hg:hg_file_finder"
        ]
    }
)
