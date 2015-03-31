#!/usr/bin/python
#
# observer.py
#
# 2015/03/29
# rg
#
# classes to implement observer pattern and observe changes that occur in specific classes


# Provide an Observable base class for any class meeting this criteria:
# - must contain a organize_data() function which prepares and returns an array of ints
#
# For future improvement (garbage collection), look towards: https://github.com/DanielSank/observed

# decorator to be used on methods that affect the state of the game. subscribes the observer to all changes made
#  to methods in the Observable class
def notify_observers(func):
    def func_wrapper(self, *args, **kwargs):
        func(self, *args, **kwargs)
        for observer in self._observers:
            observer.observe(self.organize_data())
    return func_wrapper


class Observable(object):

    def __init__(self):
        self._observers = []

    def register_observer(self, obj):
        if obj not in self._observers:
            self._observers.append(obj)


class Observer(object):
    def __init__(self, obj):
        self._observed = obj
        self.buffer = None
        self.register(obj)

    def register(self, obj):
        obj.register_observer(self)

    # store a copy of the integer list passed our way
    def observe(self, int_list):
        self.buffer = list(int_list)

    # return the ith member of the buffer. This is useful for assigning 10 neurons to the same Observer, each with id
    def get_value_by_index(self, index):
        return self.buffer[index]


class PlayerObserver(Observer):
    def __init__(self, player):
        super(PlayerObserver, self).__init__(player)

