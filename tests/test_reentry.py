import sys

import pytest

from jaraco.vcs import reentry


def hello_world():
    print("hello world")


def hello_unicode_world():
    print(b"hello world".decode('ascii'))


def exit_zero():
    raise SystemExit(0)


def exit_one():
    raise SystemExit(1)


def exit_string():
    raise SystemExit('who does this?')


def echo():
    print("args are", sys.argv)


class TestReEntry:
    """
    Test the in-process entry point launcher
    """

    def test_hello_world(self):
        with reentry.in_process_context(['hello-world.py']) as proc:
            hello_world()
        assert proc.returncode == 0
        assert proc.stdio.stdout.getvalue() == 'hello world\n'

    def test_hello_world_unicode(self):
        with reentry.in_process_context(['hello-world.py']) as proc:
            hello_unicode_world()
        assert proc.returncode == 0
        assert proc.stdio.stdout.getvalue() == 'hello world\n'

    def test_main_with_system_exit(self):
        with reentry.in_process_context(['exit-zero']) as proc:
            exit_zero()
        assert proc.returncode == 0
        assert proc.stdio.stdout.getvalue() == ''

    def test_main_with_system_exit_one(self):
        with reentry.in_process_context(['exit-one']) as proc:
            exit_one()
        assert proc.returncode == 1
        assert proc.stdio.stdout.getvalue() == ''

    def test_main_with_system_exit_string(self):
        with reentry.in_process_context(['exit-string']) as proc:
            exit_string()
        assert proc.returncode == 1
        assert proc.stdio.stdout.getvalue() == ''

    def test_echo_args(self):
        with reentry.in_process_context(['echo', 'foo', 'bar']) as proc:
            echo()
        assert proc.returncode == 0
        out = "args are ['echo', 'foo', 'bar']\n"
        assert proc.stdio.stdout.getvalue() == out


class TestErrors:
    def test_name_error(self):
        with pytest.raises(NameError) as exc_info:
            with reentry.in_process_context([]) as proc:
                not_present  # noqa
        assert proc.returncode == 1
        msg = "name 'not_present' is not defined"
        assert str(exc_info.value).endswith(msg)

    def test_keyboard_interrupt(self):
        with pytest.raises(KeyboardInterrupt):
            with reentry.in_process_context([]) as proc:
                raise KeyboardInterrupt()
        assert proc.returncode == 1
