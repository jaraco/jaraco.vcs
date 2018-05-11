# from jaraco.classes 1.4.3
def iter_subclasses(cls, _seen=None):
	"""
	Generator over all subclasses of a given class, in depth-first order.

	>>> bool in list(iter_subclasses(int))
	True
	>>> class A(object): pass
	>>> class B(A): pass
	>>> class C(A): pass
	>>> class D(B,C): pass
	>>> class E(D): pass
	>>>
	>>> for cls in iter_subclasses(A):
	...		print(cls.__name__)
	B
	D
	E
	C
	>>> # get ALL (new-style) classes currently defined
	>>> res = [cls.__name__ for cls in iter_subclasses(object)]
	>>> 'type' in res
	True
	>>> 'tuple' in res
	True
	>>> len(res) > 100
	True
	"""

	if not isinstance(cls, type):
		raise TypeError(
			'iter_subclasses must be called with '
			'new-style classes, not %.100r' % cls
		)
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
		for sub in iter_subclasses(sub, _seen):
			yield sub
