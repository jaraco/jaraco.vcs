import sys
import functools

# next statement from jaraco.compat.py25compat
try:
	next = next
except NameError:
	class __NotSupplied(object): pass
	def next(iterable, default=__NotSupplied):
		try:
			return iterable.next()
		except StopIteration:
			if default is __NotSupplied:
				raise
			return default

# namedtuple
try:
	from collections import namedtuple
except ImportError:
	# Python 2.5 compat
	from .namedtuple_backport import namedtuple

# reduce
if sys.version_info < (2,6):
	reduce = reduce
else:
	reduce = functools.reduce
