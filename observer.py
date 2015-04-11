#!/usr/bin/python
#
# observer.py
#
# 2015/03/29
# rg
#
# classes to implement observer pattern and observe changes that occur in specific classes

import uuid
from utility import *


# Provide an Observable base class for any class meeting this criteria:
# - must contain a organize_data() function which prepares and returns an array of ints
#
# For future improvement (garbage collection), look towards: https://github.com/DanielSank/observed

# decorator to be used on methods that affect the state of the game. subscribes the observer to all changes made
#  to methods in the Observable class
def notify_observers_after(func):
    def func_wrapper(self, *args, **kwargs):
        ret_value = func(self, *args, **kwargs)
        for observer in self._observers:
            observer.observe(self.organize_data())
        return ret_value
    return func_wrapper


def notify_observers_before(func):
    def func_wrapper(self, *args, **kwargs):
        for observer in self._observers:
            observer.observe(self.organize_data())
        return func(self, *args, **kwargs)

    return func_wrapper


class Observable(object):
    def __init__(self):
        self._observers = []
        self.id = uuid.uuid4()

    def register_observer(self, obj):
        if obj not in self._observers:
            self._observers.append(obj)

    # trigger a notification of observers without changing state
    @notify_observers_after
    def noop_notify(self):
        pass


class Observer(object):
    def __init__(self, obj):
        self._observed = obj
        self.register(obj)
        self.buffer = None
        self.id = uuid.uuid4()

        # fill the buffer
        self._observed.noop_notify()

        self.width = obj.observable_width

    def register(self, obj):
        obj.register_observer(self)

    # store a copy of the integer dict passed our way
    def observe(self, int_dict):
        if not int_dict:
            self.buffer = None
        else:
            self.buffer = dict(int_dict)

    # return the ith member of the buffer. This is useful for assigning 10 neurons to the same Observer, each with id
    def get_value_by_index(self, index):
        return self.buffer[index]