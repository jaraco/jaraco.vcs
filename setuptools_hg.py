"""
A plugin for setuptools to find files under the Mercurial version control
system which uses the Python library by default and falls back to use the
command line programm hg(1).
"""
__version__ = '0.1'
__author__ = 'Jannis Leidel'
__all__ = ['hg_file_finder']

import os
import subprocess

try:
    from mercurial import hg, ui, cmdutil
    from mercurial.repo import RepoError
except:
    hg = None

if os.getenv('HG_SETUPTOOLS_FORCE_CMD'):
    hg = None

def find_files_with_lib(dirname):
    """
    Use the Mercurial library to recursively find versioned files in dirname.
    """
    try:
        repo = hg.repository(ui.ui(), dirname)
    except RepoError:
        return

    # tuple of (modified, added, removed, deleted, unknown, ignored, clean)
    modified, added, removed, deleted, unknown = repo.status()[:5]

    # exclude all files that hg knows about, but haven't been added,
    # or have been deleted, removed, or have an unknown status
    excluded = removed + deleted + unknown

    rev = None
    match = cmdutil.match(repo, [], {}, default='relglob')
    match.bad = lambda x, y: False
    for abs in repo[rev].walk(match):
        if not rev and abs not in repo.dirstate:
            continue
        if abs in excluded:
            continue
        yield abs

def find_files_with_cmd(dirname="."):
    """
    Use the hg command to recursively find versioned files in dirname.
    """
    proc = subprocess.Popen(['hg', 'locate'],
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            cwd=dirname)
    stdout, stderr = proc.communicate()
    return stdout.splitlines()

def hg_file_finder(dirname="."):
    """
    Find the files in ``dirname`` under Mercurial version control.
    """
    if not dirname:
        dirname = "."
    if hg is None:
        return find_files_with_cmd(dirname)
    return find_files_with_lib(dirname)

def main():
    import sys
    from pprint import pprint
    try:
        dirname = sys.argv[1]
    except IndexError:
        dirname = "."
    pprint(list(hg_file_finder(dirname)))

if __name__ == '__main__':
    main()
