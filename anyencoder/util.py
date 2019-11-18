"""
Objects provided by this module:
    * :func:`import_chain`
    * :func:`memoize_method`
"""


from functools import wraps
from importlib import import_module
from typing import Iterable


def import_chain(modules: Iterable):
    """
    A chain-of-responsiblity that imports a module from an Iterable.

    :param modules: A sequence of module names to try importing.
    :return: The first module to successfully load.
    """
    module = None

    for m in modules:
        try:
            module = import_module(m)
            break
        except ImportError:
            continue

    if module is None:
        raise ImportError('No modules found')

    return module


def memoize_method(obj=None):
    """
    This is a method decorator which implements memoization, while
    ignoring the first argument (presumably cls or self.)
    """
    # Obnoxiously enough, functools.lru_cache:
    #  1) Doesn't seem to play nicely with classmethods (please prove
    #     me wrong.)
    #  2) Keys 'self' on instance methods, thereby busting caching as
    #     I need it to work.

    def decorator(obj):
        cache = dict()
        hits = 0
        misses = 0

        @wraps(obj)
        def wrapper(self, *args, **kwargs):
            nonlocal cache, hits, misses
            key = (args, frozenset(kwargs.items()))
            try:
                result = cache[key]
                # Cache hit
                hits += 1
            except KeyError:
                # Cache miss
                misses += 1
                result = obj(self, *args, **kwargs)
                cache[key] = result
            return result

        def _cache_stats():
            nonlocal hits, misses
            return hits, misses

        def _cache_reset():
            nonlocal cache, hits, misses
            cache.clear()
            hits, misses = 0, 0

        wrapper._cache_stats = _cache_stats
        wrapper._cache_reset = _cache_reset

        return wrapper

    return decorator if obj is None else decorator(obj)


def simple_str(obj):
    """
    This is a class decorator which adds a simple __str__ method.
    """
    def __str__(self):
        return self.__class__.__name__

    if not hasattr(obj, '__str__'):
        obj.__str__ = __str__

    return obj
