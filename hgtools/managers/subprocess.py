import os
import subprocess

from . import base
from . import cmd


class Subprocess:
	env = None

	def _invoke(self, *params):
		"""
		Invoke self.exe as a subprocess
		"""
		cmd = [self.exe] + list(params)
		proc = subprocess.Popen(
			cmd, stdout=subprocess.PIPE,
			stderr=subprocess.PIPE, cwd=self.location, env=self.env)
		stdout, stderr = proc.communicate()
		if not proc.returncode == 0:
			raise RuntimeError(stderr.strip() or stdout.strip())
		return stdout.decode('utf-8')


class MercurialManager(Subprocess, cmd.Mercurial, base.RepoManager):
	"""
	A RepoManager implemented by calling into the 'hg' command-line
	as a subprocess.
	"""
	priority = 1
	if os.path.isdir('.hg'):
		priority += 1

	@property
	def env(self):
		"""
		Return an environment safe for calling an `hg` subprocess.

		Removes MACOSX_DEPLOYMENT_TARGET from the env, as if there's a
		mismatch between the local Python environment and the environment
		in which `hg` is installed, it will cause an exception. See
		https://bitbucket.org/jaraco/hgtools/issue/7 for details.
		"""
		env = os.environ.copy()
		env.pop('MACOSX_DEPLOYMENT_TARGET', None)
		return env


class GitManager(Subprocess, cmd.Git, base.RepoManager):
	"""
	A RepoManager implemented by calling into the 'git' command-line
	as a subprocess.
	"""
	priority = 1
	if os.path.isdir('.git'):
		priority += 1
