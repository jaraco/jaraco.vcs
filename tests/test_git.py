import datetime
import os

import pytest

from jaraco import vcs
from jaraco.vcs import cmd, subprocess


def test_subprocess_manager_invalid_when_exe_missing():
    """
    If the executable dosen't exist, the manager should report
    False for .is_valid().
    """
    non_existent_exe = '/non_existent_executable'
    assert not os.path.exists(non_existent_exe)
    repo = subprocess.Git()
    repo.exe = non_existent_exe
    assert not repo.is_valid()


@pytest.mark.usefixtures("git_repo")
class TestTags:
    def test_single_tag(self):
        repo = vcs.Git('.')
        assert repo.get_tags() == set()
        repo._invoke('tag', '-am', "Tagging 1.0", '1.0')
        assert repo.get_tags() == {'1.0'}
        repo._invoke('checkout', '1.0')
        assert repo.get_tags() == {'1.0'}


class TestParseVersion:
    def test_simple(self):
        assert cmd.Git._parse_version('git version 1.9.3') == '1.9.3'

    def test_trailing_mess(self):
        val = cmd.Git._parse_version('git version 1.9.3 (Mac OS X)')
        assert val == '1.9.3'


@pytest.mark.usefixtures("git_repo")
class TestRevisionTimestamp:
    def test_tagged_rev_timestamp(self):
        repo = vcs.Git('.')
        repo._invoke('tag', '-am', 'tagging 1.0', '1.0')
        assert repo.get_timestamp('1.0').date() == datetime.date.today()


class TestIsolation:
    def test_commits_not_signed(self, git_repo):
        output = git_repo._invoke('log', '--show-signature')
        assert 'Signature made' not in output
