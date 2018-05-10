# from jaraco.util.classutil
def itersubclasses(cls, _seen=None):
	"""
	itersubclasses(cls)

	Generator over all subclasses of a given class, in depth-first order.

	>>> bool in list(itersubclasses(int))
	True
	>>> class A(object): pass
	>>> class B(A): pass
	>>> class C(A): pass
	>>> class D(B,C): pass
	>>> class E(D): pass
	>>>
	>>> for cls in itersubclasses(A):
	...		print(cls.__name__)
	B
	D
	E
	C
	>>> # get ALL (new-style) classes currently defined
	>>> [cls.__name__ for cls in itersubclasses(object)] #doctest: +ELLIPSIS
	[...'tuple', ...]
	"""

	if not isinstance(cls, type):
		raise TypeError(
			'itersubclasses must be called with '
			'new-style classes, not %.100r' % cls)
	if _seen is None:
		_seen = set()
	try:
		subs = cls.__subclasses__()
	except TypeError:  # fails only when cls is type
		subs = cls.__subclasses__(cls)
	for sub in subs:
		if sub in _seen:
			continue
		_seen.add(sub)
		yield sub
		for sub in itersubclasses(sub, _seen):
			yield sub
