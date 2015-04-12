from operator import itemgetter
import gc

# configure application-wide logging
import logging

logging.basicConfig(filename='debug.log.txt', level=logging.DEBUG)
disable_logging = True


# wrapper that respects toggling debug on/off
def log_debug(msg):
    if not disable_logging:
        log_debug(msg)


def indent_print(indent_level, str):
    print ''.join('\t' for x in range(0, indent_level)) + str


# flatten arbitrarily nested lists
# borrowed from http://stackoverflow.com/questions/10823877
def flatten(items, seqtypes=(list, tuple)):
    for i, x in enumerate(items):
        while isinstance(items[i], seqtypes):
            items[i:i + 1] = items[i]
    return items


# borrowed from http://stackoverflow.com/questions/31875
# noinspection PyPep8Naming,PyAttributeOutsideInit
class Singleton:
    """
    A non-thread-safe helper class to ease implementing singletons.
    This should be used as a decorator -- not a metaclass -- to the
    class that should be a singleton.

    The decorated class can define one `__init__` function that
    takes only the `self` argument. Other than that, there are
    no restrictions that apply to the decorated class.

    To get the singleton instance, use the `Instance` method. Trying
    to use `__call__` will result in a `TypeError` being raised.

    Limitations: The decorated class cannot be inherited from.

    Usage example:
    f = Foo.Instance()
    g = Foo.Instance()
    print f is g # True

    """

    def __init__(self, decorated):
        self._decorated = decorated

    def Instance(self):
        """
        Returns the singleton instance. Upon its first call, it creates a
        new instance of the decorated class and calls its `__init__` method.
        On all subsequent calls, the already created instance is returned.

        """
        try:
            return self._instance
        except AttributeError:
            self._instance = self._decorated()
            return self._instance

    def __call__(self):
        raise TypeError('Singletons must be accessed through `Instance()`.')

    def __instancecheck__(self, inst):
        return isinstance(inst, self._decorated)

import cPickle


def memoized(f):
    """ Memoization decorator for functions taking one or more arguments. """
    class memodict(dict):
        def __init__(self, func):
            self.func = func
            self.last_args = None

        def __call__(self, *args):
            self.last_args = args
            hash_key = memodict.make_key(args)
            return self[hash_key]

        def __missing__(self, hash_key):
            if self.last_args is None:
                raise Exception("no stored args to work with")
            else:
                ret = self[hash_key] = self.func(*self.last_args)
                self.last_args = None
                return ret

        # http://stackoverflow.com/a/3296318/2023776
        def __get__(self, obj, objtype):
            """Support instance methods."""
            import functools
            return functools.partial(self.__call__, obj)

        @staticmethod
        def make_key(args):
            hash_string = ""
            for arg in args:
                try:
                    hash_string += arg.__repr__()
                except:
                    hash_string += cPickle.dumps(arg)

            return hash(hash_string)

    return memodict(f)