from operator import itemgetter
import gc

# configure application-wide logging
import logging

logging.basicConfig(filename='debug.log.txt', level=logging.DEBUG)

enable_logging_debug = False
enable_logging_info = False
enable_logging_warn = True


# wrapper that respects toggling debug on/off
def log_debug(msg):
    if enable_logging_debug:
        logging.debug(msg)


def log_info(msg):
    if enable_logging_info:
        logging.info(msg)


def log_warn(msg):
    if enable_logging_warn:
        logging.warn(msg)


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
from pylru import lrucache
from functools import wraps


class memoized(object):
    """ Memoization decorator for functions taking one or more arguments. """

    def __init__(self, maxsize=128):
        self.cache = lrucache(maxsize)

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = memoized.make_key(args, kwargs)
            try:
                return self.cache[key]
            except KeyError:
                pass

            value = func(*args, **kwargs)
            self.cache[key] = value
            return value

        return wrapper

    @staticmethod
    def make_key(args, kwargs):
        hash_string = ""
        for arg in args:
            try:
                hash_string += arg.__repr__()
            except:
                hash_string += cPickle.dumps(arg)

        for key in sorted(kwargs.keys()):
            try:
                hash_string += key + kwargs[key].__repr__()
            except:
                hash_string += key + cPickle.dumps(kwargs[key])

        return hash(hash_string)