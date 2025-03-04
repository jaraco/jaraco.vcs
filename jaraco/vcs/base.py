"""
This project implements several repo implementations, each of which provides
an interface to source code repository functionality.
"""

from __future__ import annotations

import itertools
import os.path
import posixpath
from collections.abc import Iterable

import dateutil.parser
from more_itertools import one

import jaraco.versioning as versioning
from jaraco.classes.ancestry import iter_subclasses


class Repo(versioning.VersionManagement):
    """
    An abstract class defining some interfaces for working with
    repositories.
    """

    def __init__(self, location='.'):
        self.location = location
        self.setup()

    def is_valid(self):
        "Return True if this instance is a valid for this location."
        return True

    def setup(self):
        pass

    @classmethod
    def get_valid_managers(cls, location):
        """
        Get the valid Repo implementations for this location.
        """

        def by_priority_attr(c):
            return getattr(c, 'priority', 0)

        classes = sorted(iter_subclasses(cls), key=by_priority_attr, reverse=True)
        instances = (c(location) for c in classes)
        return (inst for inst in instances if inst.is_valid())

    @staticmethod
    def detect(location='.'):
        try:
            return next(Repo.get_valid_managers(location))
        except StopIteration as e:
            e.args = ("No source repo or suitable VCS version found",)
            raise

    @staticmethod
    def existing_only(instances: Iterable[Repo]):
        """
        Return only those instances that refer to an existing repo
        """
        return (inst for inst in instances if inst.find_root())

    def __repr__(self):
        return '{self.__class__.__name__}({self.location})'.format(**vars())

    def find_root(self):
        raise NotImplementedError()

    def find_files(self):
        raise NotImplementedError()

    def get_tags(self, rev=None):
        """
        Get the tags for the specified revision (or the current revision
        if none is specified).
        """
        raise NotImplementedError()

    def get_repo_tags(self):
        """
        Get all tags for the repository.
        """
        raise NotImplementedError()

    def get_parent_tags(self, rev=None):
        """
        Return the tags for the parent revision (or None if no single
            parent can be identified).
        """
        try:
            parent_rev = one(self.get_parent_revs(rev))
        except Exception:
            return None
        return self.get_tags(parent_rev)

    def get_parent_revs(self, rev=None):
        """
        Get the parent revision for the specified revision (or the current
        revision if none is specified).
        """
        raise NotImplementedError

    def is_modified(self):
        'Does the current working copy have modifications'
        raise NotImplementedError()

    def find_all_files(self):
        """
        Find files including those in subrepositories.
        """
        files = self.find_files()
        subrepo_files = (
            posixpath.join(subrepo.location, filename)
            for subrepo in self.subrepos()
            for filename in subrepo.find_files()
        )
        return itertools.chain(files, subrepo_files)

    def subrepos(self):
        paths = (os.path.join(self.location, path) for path in self.sub_paths())
        return map(self.__class__, paths)

    def sub_paths(self):
        raise NotImplementedError()

    def get_timestamp(self, rev):
        return dateutil.parser.parse(self._get_timestamp_str(rev))

    def age(self):
        """
        Return the age of the repo.
        """
        raise NotImplementedError()

    def commit_tree(self, spec, msg="committed"):
        """
        Apply the tree in spec and commit.
        """
        raise NotImplementedError()

    def describe_version(self):
        """
        Return a string representing a version of the current state.
        """
        raise NotImplementedError()
