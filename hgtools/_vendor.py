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
            'iter_subclasses must be called with ' 'new-style classes, not %.100r' % cls
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


# from more_itertools 4.1.0
def one(iterable, too_short=None, too_long=None):
    """Return the first item from *iterable*, which is expected to contain only
    that item. Raise an exception if *iterable* is empty or has more than one
    item.
    :func:`one` is useful for ensuring that an iterable contains only one item.
    For example, it can be used to retrieve the result of a database query
    that is expected to return a single row.
    If *iterable* is empty, ``ValueError`` will be raised. You may specify a
    different exception with the *too_short* keyword:

    >>> it = []
    >>> one(it)  # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ...
    ValueError: too many items in iterable (expected 1)'
    >>> too_short = IndexError('too few items')
    >>> one(it, too_short=too_short)  # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ...
    IndexError: too few items

    Similarly, if *iterable* contains more than one item, ``ValueError`` will
    be raised. You may specify a different exception with the *too_long*
    keyword:

    >>> it = ['too', 'many']
    >>> one(it)  # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ...
    ValueError: too many items in iterable (expected 1)'
    >>> too_long = RuntimeError
    >>> one(it, too_long=too_long)  # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ...
    RuntimeError

    Note that :func:`one` attempts to advance *iterable* twice to ensure there
    is only one item. If there is more than one, both items will be discarded.
    See :func:`spy` or :func:`peekable` to check iterable contents less
    destructively.
    """
    it = iter(iterable)

    try:
        value = next(it)
    except StopIteration:
        raise too_short or ValueError('too few items in iterable (expected 1)')

    try:
        next(it)
    except StopIteration:
        pass
    else:
        raise too_long or ValueError('too many items in iterable (expected 1)')

    return value
