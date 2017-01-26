6.5
===

* Issue #31: Add support for Git-backed Mercurial repositories with
  bookmarks on the tip.

6.4
===

* Moved hosting to Github.

6.3
===

* Updated 'dev' revision to be compatible with setuptools 8 canonical
  pre-release version numbering (now '.dev0').

6.2.1
=====

* Pull Request #7: Fixed intermittent test failures.

6.2
===

* Issue #28: Fixed poor parsing of git version. Also provide a nicer error
  message when no repo manager is found.
* Added support for querying the Mercurial version in cmd.Mercurial.

6.1
===

* Issue #21: GitManager is now only valid if Git 1.7.10 or later is present.

6.0
===

* Issue #23: hgtools no longer imports Mercurial and thus does not link to
  it. Applications that wish to use the in-process Mercurial manager must
  first `import mercurial.dispatch` in their application.
* Issue #23: hgtools is now licensed under the MIT license.

5.3
===

* Issue #19: Add file finder support for git. Credit to Berry Phillips.

5.2
===

* Issue #20: Added support for listing all git tags. Credit to Berry Phillips.

5.1
===

* In version inference, always fallback to increment (or None) when an
  Exception occurs in the calculation.

5.0.1
=====

* Issue #17: Fix regression on older versions of setuptools where unspecified
  distribution attributes would cause use_vcs_version of None to supersede
  a supplied use_hg_version.

5.0
===

* Added new ``use_vcs_version`` distutils parameter to supersede
  ``use_hg_version``. Clients should update to use this new parameter as soon
  as hgtools 5.0 is generally available.
* Initial git support. The tool now nominally supports eliciting the project
  version from a git tag. Many of the hg features are not yet implemented,
  such as auto-incrementing versions when the current revision is not on a
  tag and file discovery from repo metadata.
  This new Git support provides experimental support for dual-hosted
  repositories (such as those found on Kiln). Since file discovery is not yet
  tested or implemented, there are likely to be yet undiscovered issues.
* Refactored the Manager models to better support the two repositories.
  Clients that use hgtools to programmatically manipulate repositories will
  need to update to use the new names. In particular, HGRepoManager was
  renamed to RepoManager. SubprocessManager renamed to MercurialManager and
  a new GitManager was created. The LibraryManager was renamed to
  MercurialInProcManager.

4.0
===

* Removed functions in hgtools (package) module deprecated since 0.6.6.

3.0.2
=====

* Restored Python 2.6 compatibility in reentry module.

3.0.1
=====

* Merged changes from 2.2.2 to address #13.

3.0
===

* Removed support for Python 2.5. Python 2.6 or later is now required.

2.2.3
=====

* Restored Python 2.5 compatibility in some modules.

2.2.2
=====

* Removed the LibraryManager from the default imports. This means it will not
  be available unless the client application specifically imports
  `hgtools.managers.library`. This change appears to fix #13.

2.2.1
=====

* Added some exception handling and tests around Library Manager in the hopes
  of preventing #13.

2.2
===

* LibraryManager has been re-written to use the command-line API in-process.
  The new LibraryManager now only works Python 2.7 and greater, but also now
  shares the same capability as the SubprocessManager with full tags support.

2.1
===

* hgtools now builds natively on Python 3, rather than requiring a 2to3
  conversion at install time.

2.0.3
=====

 * Issue #12: Suppress exceptions besides ImportError when importing
   Mercurial modules.

2.0.2
=====

* Force `hg log` and `hg parents` to use the defaults style for output.
  Otherwise, the parsing code fails to identify the tags. Also, reset the
  'default.log' value in case a user has an alias for `hg log` in his .hgrc.
  (For example, some use log=-G to force the graph output). Thanks to
  `dc <https://bitbucket.org/dc>`_ for the patch.

2.0.1
=====

* Fixed issue #10 where hgtools would not parse setup.cfg properly if
  the Python 3 configparser backport was installed on Python 2.

2.0
===

* Refactored HGRepoManager to better support multiple tags:

  - `.get_tag` replaced by `.get_tags`, which returns a set of tags
    for a specific revision. This is currently a set because mercurial
    does not retain any meaningful order of the tags.
  - `.get_tags` replaced by `.get_repo_tags`.
  - `.get_parent_tag` replaced by `.get_parent_tags`.
  - added `.get_parents` which returns the revision(s) of the specified
    revision.

* Removed support for older versions of mercurial (LegacyLibraryManager).
* The subprocess manager is now the default. The HGTOOLS_FORCE_CMD variable
  no longer has any effect on hgtools.
* Version detection now resolves multiple tags on the same revision by
  choosing the greatest version.

1.2.1
=====

* Fix issue #9 - The repo managers and thus the setuptools plugin will no
  longer find files that aren't in the location specified. The
  LibraryManagers already will throw an error in this case, but now the
  SubprocessManager does what's best and only returns files relative
  to the location.

1.2
===

* Implemented the `version_handler` version parameter. Fixes #5.
* If multiple tags are given for a revision, the last tag is used instead
  of the first.

1.1.6
=====

* More aggressively construct a the environment when running `hg` in a
  subprocess. Fixes another manifestation of #7. Thanks whit537.

1.1.5
=====

* Fix issue #8 - Re-wrote SubprocessManager.get_tag to extract the tag using
  `hg tags` for more reliable tag resolution.

1.1.3
=====

* Fix issue #7 - SubprocessManager now passes explicit environment to child
  process.

1.1.2
=====

* Restored Python 2.5 compatibility.

1.1
===

* Added support for subrepos. The setuptools plugin will now traverse
  subrepos when finding files.

1.0.1
=====

* Fix issue #6 where the force_hg_version flag was affecting installation
  of tagged packages not employing hgtools.

1.0
===

* Python 3 support
* Now supports revisions with multiple tags (chooses the first, which
  appears to be the latest).
* Removed support for deprecated use_hg_version_increment.
* Added HGRepoManager.existing_only to filter managers for only those
  which refer to an existing repo.
* Employed HGRepoManager.existing_only in plugins. Fixes #2.
* SubprocessManager no longer writes to /dev/null. Fixes #3.

0.6.7
=====

* Auto-versioning will no longer use the parent tag if the working
  copy has modifications.

0.6.6
=====

* Some minor refactoring - moved functions out of top-level `hgtools`
  module into hgtools.plugins.

0.6.5
=====

 * Test case and fix for error in SubprocessManager when 'hg'
   executable doesn't exist.

0.6.4
=====

 * Fix for NameError created in 0.6.3.

0.6.3
=====

 * Deprecated use_hg_version_increment setup parameter in favor of
   parameters to use_hg_version.

0.6.2
=====

 * From drakonen: hgtools will now utilize the parent changeset tag
   for repositories that were just tagged (no need to update to that
   tag to release).

0.6.1
=====

 * Fixed issue #4: Tag-based autoversioning fails if hgrc defaults
   used for hg identify

0.6
===

 * Refactored modules. Created ``managers``, ``versioning``, and
   ``py25compat`` modules.

0.5.2
=====

 * Yet another fix for #1. It appears that simply not activating the
   function is not sufficient. It may be activated by previously-
   installed packages, so it needs to be robust for non-hgtools
   packages.

0.5.1
=====

 * Fix for issue #1 - version_calc_plugin is activated for projects that
   never called for it.
 * LibraryManagers no longer raise errors during the import step
   (instead, they just report as being invalid).
 * SubprocessManager now raises a RuntimeError if the executed command
   does not complete with a success code.

0.5
===

 * Fixed issue in file_finder_plugin where searching for an
   appropriate manager would fail if mercurial was not installed in
   the Python instance (ImportErrors weren't trapped properly).

0.4.9
=====

 * Fixed issue where version calculation would fail if tags contained
   spaces.

0.4.8
=====

 * Auto versioning now provides a reasonable default when no version
   tags are yet present.

0.4.3-0.4.7
===========

 * Fixes for versions handling of hgtools itself.

0.4.2
=====

 * Fixed formatting errors in documentation.

0.4.1
=====

 * Reformatted package layout so that other modules can be included.
 * Restored missing namedtuple_backport (provides Python 2.5 support).

0.4
===

 * First release supporting automatic versioning using mercurial tags.
