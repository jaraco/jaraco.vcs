from __future__ import print_function

import sys

from hgtools.managers import library as reentry

def hello_world():
	print("hello world")

def exit_zero():
	raise SystemExit(0)

def exit_one():
	raise SystemExit(1)

def exit_string():
	raise SystemExit('who does this?')

def echo():
	print("args are", sys.argv)

class TestReEntry(object):
	"""
	Test the in-process entry point launcher
	"""
	def test_hello_world(self):
		with reentry.in_process_context(['hello-world.py']) as proc:
			hello_world()
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
