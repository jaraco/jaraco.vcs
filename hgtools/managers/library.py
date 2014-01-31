from __future__ import absolute_import

from . import base
from . import cmd
from . import reentry

try:
	import mercurial.__version__
	import mercurial.dispatch
except ImportError:
	pass
except Exception:
	pass

class MercurialInProcManager(cmd.Mercurial, base.RepoManager):
	"""
	A RepoManager implemented by invoking the hg command in-process.
	"""

	def _invoke(self, *params):
		"""
		Run the self.exe command in-process with the supplied params.
		"""
		cmd = [self.exe, '-R', self.location] + list(params)
		with reentry.in_process_context(cmd) as result:
			mercurial.dispatch.run()
		stdout = result.stdio.stdout.getvalue()
		stderr = result.stdio.stderr.getvalue()
		if not result.returncode == 0:
			raise RuntimeError(stderr.strip() or stdout.strip())
		return stdout.decode('utf-8')
