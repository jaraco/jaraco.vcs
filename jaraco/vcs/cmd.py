import abc
import itertools
import operator
import os.path
import re
import subprocess
import types
import typing

import dateutil.parser
from tempora import utc

import jaraco.path


class TaggedRevision(typing.NamedTuple):
    tag: str
    revision: str


class Command(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def _invoke(self, *args): ...

    def is_valid(self):
        try:
            # Check if both command and repo are valid
            self._invoke('status')
        except Exception:
            return False
        return super().is_valid()

    def version(self):
        """
        Return the underlying version
        """
        lines = iter(self._invoke('version').splitlines())
        version = next(lines).strip()
        return self._parse_version(version)

    @classmethod
    def _parse_version(cls, version):
        return re.search(cls.version_pattern, version).group(1)


class Mercurial(Command):
    exe = 'hg'
    version_pattern = r'Mercurial Distributed SCM \((.*?)\)'

    def find_root(self):
        try:
            return self._invoke('root').strip()
        except Exception:
            pass

    def find_files(self):
        """
        Find versioned files in self.location
        """
        cmd = 'locate', '-I', '.', '--config', 'ui.relative-paths=yes'
        return self._invoke(*cmd).splitlines()

    def get_parent_revs(self, rev=None):
        cmd = ['parents', '--style', 'default', '--config', 'defaults.parents=']
        if rev:
            cmd.extend(['--rev', str(rev)])
        out = self._invoke(*cmd)
        cs_pat = r'^changeset:\s+(?P<local>\d+):(?P<hash>[0-9a-zA-Z]+)'
        return (match.groupdict()['local'] for match in re.finditer(cs_pat, out))

    def get_tags(self, rev=None):
        """
        Get the tags for the given revision specifier (or the
        current revision if not specified).
        """
        rev_num = self._get_rev_num(rev)
        # rev_num might end with '+', indicating local modifications.
        return (
            set(self._read_tags_for_rev(rev_num))
            if not rev_num.endswith('+')
            else set()
        )

    def _read_tags_for_rev(self, rev_num):
        """
        Return the tags for revision sorted by when the tags were
        created (latest first)
        """
        return (tr.tag for tr in self._read_tags_for_revset(rev_num))

    def _read_tags_for_revset(self, spec):
        """
        Return TaggedRevision for each tag/rev combination in the revset spec
        """
        cmd = ['log', '--style', 'default', '--config', 'defaults.log=', '-r', spec]
        res = self._invoke(*cmd)
        header_pattern = re.compile(r'(?P<header>\w+?):\s+(?P<value>.*)')
        match_res = map(header_pattern.match, res.splitlines())
        matched_lines = filter(None, match_res)
        matches = (match.groupdict() for match in matched_lines)
        for match in matches:
            if match['header'] == 'changeset':
                id, sep, rev = match['value'].partition(':')
            if match['header'] == 'tag':
                tag = match['value']
                yield TaggedRevision(tag, rev)

    def _get_rev_num(self, rev=None):
        """
        Determine the revision number for a given revision specifier.
        """
        # first, determine the numeric ID
        cmd = ['identify', '--num']
        # workaround for #4
        cmd.extend(['--config', 'defaults.identify='])
        if rev:
            cmd.extend(['--rev', rev])
        res = self._invoke(*cmd)
        return res.strip()

    def _get_tags_by_num(self):
        """
        Return a dictionary mapping revision number to tags for that number.
        """
        by_revision = operator.attrgetter('revision')
        tags = sorted(self.get_tags(), key=by_revision)
        revision_tags = itertools.groupby(tags, key=by_revision)

        def get_id(rev):
            return rev.split(':', 1)[0]

        return {
            get_id(rev): [tr.tag for tr in tr_list] for rev, tr_list in revision_tags
        }

    def get_repo_tags(self):
        lines = self._invoke('tags').splitlines()
        return (TaggedRevision(*line.rsplit(None, 1)) for line in lines if line)

    def get_ancestral_tags(self, rev='.'):
        """
        Like get_repo_tags, but only get those tags ancestral to the current
        changeset.
        """
        spec = 'sort(ancestors({rev}), -date)'.format(**vars())
        return self._read_tags_for_revset(spec)

    def is_modified(self):
        out = self._invoke('status', '-mard')
        return bool(out)

    def sub_paths(self):
        try:
            with open(os.path.join(self.location, '.hgsub')) as file:
                return [line.partition('=')[0].strip() for line in file]
        except Exception:
            return ()

    def _get_timestamp_str(self, rev):
        return self._invoke('log', '-l', '1', '--template', '{date|isodate}', '-r', rev)

    def commit_tree(self, spec, message: str = 'committed'):
        jaraco.path.build(spec)
        self._invoke('addremove')
        self._invoke('commit', '-m', message)


class Git(Command):
    exe = 'git'
    version_pattern = r'git version (\d+\.\d+[^ ]*)'

    def is_valid(self):
        return super().is_valid()

    def find_root(self):
        try:
            return self._invoke('rev-parse', '--top-level').strip()
        except Exception:
            pass

    def find_files(self):
        all_files = self._invoke('ls-files').splitlines()
        return all_files

    def get_tags(self, rev=None):
        """
        Return the tags for the current revision as a set
        """
        rev = rev or 'HEAD'
        return set(self._invoke('tag', '--points-at', rev).splitlines())

    def get_repo_tags(self):
        cmd = [
            "for-each-ref",
            "--sort=-committerdate",
            "--format=%(refname:short) %(objectname:short)",
            "refs/tags",
        ]

        lines = self._invoke(*cmd).splitlines()
        return (TaggedRevision(*line.rsplit(None, 1)) for line in lines if line)

    def is_modified(self):
        """
        Is the current state modified? (currently stubbed assuming no)
        """
        return False

    def get_ancestral_tags(self, rev=None):
        """
        Like get_repo_tags, but only get those tags ancestral to the current
        changeset.
        """
        rev = rev or 'HEAD'
        matches = self._invoke('tags', '--merged', rev).splitlines()
        return (rev for rev in self.get_repo_tags() if rev.tag in matches)

    def sub_paths(self):
        lines = self._invoke('submodules', 'status').splitlines()
        return (line.split()[1] for line in lines)

    def _get_timestamp_str(self, rev):
        return self._invoke('log', '-1', '--format=%ai', rev)

    def age(self):
        """
        >>> repo = getfixture('git_repo')
        >>> repo.age()
        datetime.timedelta(...)
        """
        proc = subprocess.Popen(
            ['git', 'log', '--reverse', '--pretty=%ad', '--date', 'iso'],
            stdout=subprocess.PIPE,
            text=True,
            encoding='utf-8',
        )
        first_line = proc.stdout.readline().strip()
        proc.terminate()
        proc.wait()
        proc.stdout.close()
        return utc.now() - dateutil.parser.parse(first_line)

    def commit_tree(self, spec, message: str = 'committed'):
        jaraco.path.build(spec)
        self._invoke('add', '.')
        self._invoke('commit', '-m', message)

    def head_date(self):
        out = self._invoke(
            '-c',
            'log.showSignature=false',
            'log',
            '-n',
            '1',
            'HEAD',
            '--format=%cI',
        )
        return dateutil.parser.parse(out)

    def describe_version(self):
        """
        >>> repo = getfixture('git_repo')
        >>> _ = repo._invoke('tag', 'v1.0.0')
        >>> desc = repo.describe_version()
        >>> list(vars(desc))
        ['date', 'tag', 'distance', 'node', 'dirty']
        >>> desc.tag
        'v1.0.0'
        >>> desc.node
        'g...'
        >>> desc.distance
        0
        >>> desc.dirty
        False
        >>> repo.commit_tree({'bar': {'baz': 'new content'}})
        >>> desc = repo.describe_version()
        >>> desc.distance
        1
        >>> desc.dirty
        False
        >>> jaraco.path.build({'bar': {'baz': 'pending'}})
        >>> desc = repo.describe_version()
        >>> desc.distance
        1
        >>> desc.dirty
        True
        """
        output = self._invoke(
            'describe',
            '--dirty',
            '--tags',
            '--long',
            '--match',
            '*[0-9]*',
        )
        match = re.match(
            r'(?P<tag>.*?)-'
            r'(?P<distance>\d+)-'
            r'(?P<node>g[0-9A-Fa-f]+)'
            r'(-(?P<dirty>dirty))?',
            output,
        )
        desc = types.SimpleNamespace(date=self.head_date(), **match.groupdict())
        desc.distance = int(desc.distance)
        desc.dirty = bool(desc.dirty)
        return desc
