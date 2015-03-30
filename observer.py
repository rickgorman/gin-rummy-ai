#!/usr/bin/python
#
# observer.py
#
# 2015/03/29
# rg
#
# classes to implement observer pattern and observe changes that occur in specific classes


# provide an Observable wrapper for any class
# borrowed from http://stackoverflow.com/questions/13528213
class Observable(object):
    __initialized = False

    def __init__(self, wrapped):

        self.wrapped = wrapped
        self._callbacks = []
        self.__initialized = True

    def __getattr__(self, name):
        if self.__initialized:
            res = self.wrapped.__getattribute__(name)
            if not callable(res):
                return res

            def wrap(*args, **kwargs):
                for callback in self._callbacks:
                    callback(self.wrapped, *args, **kwargs)
                return res(*args, **kwargs)
            return wrap
        else:
            return object.__getattribute__(self, name)

    def __setattr__(self, key, value):
        if self.__initialized:
            for callback in self._callbacks:
                callback(self.wrapped)

            # assume that __setattr__ is the same in our wrapped class as it is in object
            object.__setattr__(self.wrapped, key, value)
        else:
            object.__setattr__(self, key, value)

    def __str__(self):
        return self.wrapped.__str__()

    # add a callback to obj's observe() method
    def register_observer(self, obj):
        if obj.observe not in self._callbacks:
            self._callbacks.append(obj.observe)


class Observer(object):
    def __init__(self, obj):
        self._observed = obj
        self.register(obj)

    # called by observed object. provides the observer with a list of integers
    def observe(self, int_list):
        raise NotImplementedError("must implement observe")

    def register(self, obj):
        obj.register_observer(self)


class PlayerObserver(Observer):
    def __init__(self, player):
        super(Observer, self).__init__(player)

    def observe(self, int_list):
        pass