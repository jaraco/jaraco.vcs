import sys

from . import base, cmd, reentry


class Mercurial(cmd.Mercurial, base.Repo):
    """
    A Repo implemented by invoking the hg command in-process.
    """

    def _invoke(self, *params):
        """
        Run the self.exe command in-process with the supplied params.
        """
        cmd = [self.exe, '-R', self.location] + list(params)
        with reentry.in_process_context(cmd) as result:
            sys.modules['mercurial.dispatch'].run()
        stdout = result.stdio.stdout.getvalue()
        stderr = result.stdio.stderr.getvalue()
        if not result.returncode == 0:
            raise RuntimeError(stderr.strip() or stdout.strip())
        return stdout.decode('utf-8')
