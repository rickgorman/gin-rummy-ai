#!/usr/bin/python
#
# observer.py
#
# 2015/03/29
# rg
#
# classes to implement observer pattern and observe changes that occur in specific classes


# provide an Observer wrapper for any class
# borrowed from http://stackoverflow.com/questions/13528213
class Wrapper(object):
    __initialized = False

    def __init__(self, wrapped):

        self.wrapped = wrapped
        self.callbacks = []
        self.__initialized = True

    def __getattr__(self, name):
        if self.__initialized:
            res = self.wrapped.__getattribute__(name)
            if not callable(res):
                return res

            def wrap(*args, **kwargs):
                for callback in self.callbacks:
                    callback(self.wrapped, *args, **kwargs)
                return res(*args, **kwargs)
            return wrap
        else:
            return object.__getattribute__(self, name)

    def __setattr__(self, key, value):
        if self.__initialized:
            for callback in self.callbacks:
                callback(self.wrapped)

            # assume that __setattr__ is the same in our wrapped class as it is in object
            object.__setattr__(self.wrapped, key, value)
        else:
            object.__setattr__(self, key, value)

    def __str__(self):
        return self.wrapped.__str__()

    def add_callback(self, callback):
        self.callbacks.append(callback)
