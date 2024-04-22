import datetime
import operator
import os
import platform

import pytest

from jaraco import vcs
from jaraco.vcs import subprocess


@pytest.fixture(autouse=True)
def configure_username(monkeypatch):
    """
    Some environments (Windows on Azure) have Mercurial installed
    but not configured in a way that it can commit files, because
    the username isn't configured correctly. Monkeypatch the
    class to bypass this issue.
    """
    if platform.system() != 'Windows':
        return

    def _invoke(self, *params):
        params = ('--config', 'ui.username=tester') + params
        return super(subprocess.Mercurial, self)._invoke(*params)

    monkeypatch.setattr(subprocess.Mercurial, '_invoke', _invoke)


def test_subprocess_manager_invalid_when_exe_missing():
    """
    If the hg executable dosen't exist, the manager should report
    False for .is_valid().
    """
    non_existent_exe = '/non_existent_executable'
    assert not os.path.exists(non_existent_exe)
    mgr = subprocess.Mercurial()
    mgr.exe = non_existent_exe
    assert not mgr.is_valid()


@pytest.mark.usefixtures("hg_repo")
class TestRelativePaths:
    """
    Issue #9 demonstrated that the Manager would inadvertently return too many
    files when location is not the root of the repo. This test demonstrates
    the expected behavior.
    """

    def test_nested_child(self):
        test_mgr = vcs.Mercurial('.')
        assert test_mgr.find_files() == [os.path.join('bar', 'baz')]

    def test_manager_in_child(self):
        test_mgr = vcs.Mercurial('bar')
        assert test_mgr.find_files() == ['baz']

    def test_current_dir_in_child(self):
        os.chdir('bar')
        test_mgr = vcs.Mercurial('.')
        assert test_mgr.find_files() == ['baz']


@pytest.mark.usefixtures("hg_repo")
class TestTags:
    def setup_method(self, method):
        self.mgr = vcs.Mercurial('.')

    def teardown_method(self, method):
        del self.mgr

    def test_single_tag(self):
        self.mgr._invoke('tag', '1.0')
        assert self.mgr.get_tags() == {'tip'}
        self.mgr._invoke('update', '1.0')
        assert self.mgr.get_tags() == {'1.0'}

    def test_no_tags(self):
        "No tag should return empty set"
        assert self.mgr.get_tags('0') == set()

    def test_local_modifications(self):
        "Local modifications should return empty set"
        with open('bar/baz', 'w', encoding='utf-8') as f:
            f.write('changed')
        assert self.mgr.get_tags() == set()

    def test_parent_tag(self):
        self.mgr._invoke('tag', '1.0')
        assert self.mgr.get_tags() == {'tip'}
        assert self.mgr.get_parent_tags() == {'tip'}
        assert self.mgr.get_parent_tags('.') == {'1.0'}
        assert self.mgr.get_parent_tags('tip') == {'1.0'}
        self.mgr._invoke('tag', '1.1')
        assert self.mgr.get_tags() == {'tip'}
        assert self.mgr.get_parent_tags() == {'tip'}
        assert self.mgr.get_parent_tags('.') == {'1.1'}
        assert self.mgr.get_parent_tags('tip') == {'1.1'}

    def test_two_tags_same_revision(self):
        """
        Always return the latest tag for a given revision
        """
        self.mgr._invoke('tag', '1.0')
        self.mgr._invoke('tag', '-r', '1.0', '1.1')
        self.mgr._invoke('update', '1.0')
        assert set(self.mgr.get_tags()) == {'1.0', '1.1'}

    def test_two_tags_same_revision_lexicographically_earlier(self):
        """
        Always return the latest tag for a given revision
        """
        self.mgr._invoke('tag', '1.9')
        self.mgr._invoke('tag', '-r', '1.9', '1.10')
        self.mgr._invoke('update', '1.9')
        assert set(self.mgr.get_tags()) == {'1.9', '1.10'}

    def _setup_branchy_tags(self):
        """
        Create two heads, one which has a 1.0 tag and a different one which
        has a 1.1 tag.
        """
        # create a commit with a tag
        with open('bar/baz', 'a', encoding='utf-8') as f:
            f.write('\nmore to say\n')
        self.mgr._invoke('commit', '-m', 'Had more to say')
        self.mgr._invoke('tag', '1.0')
        # update to the pre-tagged revision
        self.mgr._invoke('update', '1')
        # Make a different commit
        with open('bar/baz', 'a', encoding='utf-8') as f:
            f.write('\na different concept\n')
        self.mgr._invoke('commit', '-m', 'A different approach')
        self.mgr._invoke('tag', '1.1')

    def test_ancestral_tags_local(self):
        """
        get_ancestral_tags should only return tagged revisions ancestral
        to the current revision.
        """
        self._setup_branchy_tags()
        tag_revs = self.mgr.get_ancestral_tags()
        tags = map(operator.attrgetter('tag'), tag_revs)
        # Two tags expected, one is the specified tag and
        # the other is 'tip'. On fast hardware, the
        # timestamps for these may be close enough that
        # mercurial doesn't sort them properly by time,
        # so normalize order.
        assert sorted(tags) == ['1.1', 'tip']

    def test_ancestral_tags_specified(self):
        """
        get_ancestral_tags should only return tagged revisions ancestral
        to the specified revision.
        """
        self._setup_branchy_tags()
        (tag,) = self.mgr.get_ancestral_tags(3)
        assert tag.tag == '1.0'


@pytest.mark.usefixtures("hg_repo")
class TestRevisionTimestamp:
    def test_tagged_rev_timestamp(self):
        mgr = vcs.Mercurial('.')
        mgr._invoke('tag', '1.0')
        assert mgr.get_timestamp('1.0').date() == datetime.date.today()
