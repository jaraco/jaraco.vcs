import os
import subprocess

from . import base, cmd


class Subprocess:
    env = None

    def _invoke(self, *params):
        """
        Invoke self.exe as a subprocess
        """
        cmd = [self.exe] + list(params)
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=self.location,
            env=self.env,
        )
        stdout, stderr = proc.communicate()
        if not proc.returncode == 0:
            raise RuntimeError(stderr.strip() or stdout.strip())
        return stdout.decode('utf-8')


class Mercurial(Subprocess, cmd.Mercurial, base.Repo):
    """
    A Repo implemented by calling into the 'hg' command-line
    as a subprocess.
    """

    priority = 1 + os.path.isdir('.hg')


class Git(Subprocess, cmd.Git, base.Repo):
    """
    A Repo implemented by calling into the 'git' command-line
    as a subprocess.
    """

    priority = 1 + os.path.isdir('.git')
