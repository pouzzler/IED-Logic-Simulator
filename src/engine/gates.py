#!/usr/bin/env python3
# coding: utf-8


# TODO: increase delay when more than two inputs


"""
Builtin gates. Unlike user circuits, their evalfun() is implemented.
For scheduling: we compute the output value at present time and schedule the
change.
"""


from .simulator import *


class NotGate(Circuit):
    """One input only. Output == not Input."""
    delay = 2

    def __init__(self, name, owner, category=None):
        Circuit.__init__(self, name, owner)
        Plug(True, None, self)
        Plug(False, None, self)
        self.init_inputs()

    def evalfun(self):
        val = not self.inputList[0].value
        if self.inputList[0].value is None:
            val = None
        agenda_.schedule(self, lambda: self.outputList[0].set(val))


class AndGate(Circuit):
    """Any number of inputs. Output false unless every input true."""
    delay = 3

    def __init__(self, name, owner, inputs=2):
        Circuit.__init__(self, name, owner)
        for i in range(inputs):
            Plug(True, None, self)
        Plug(False, None, self)
        self.init_inputs()

    def evalfun(self):
        val = all([inp.value for inp in self.inputList])
        for inp in self.inputList:
            if inp.value is None and val:
                val = None
        agenda_.schedule(self, lambda: self.outputList[0].set(val))


class NandGate(Circuit):
    """Any number of inputs. Output true unless every input true."""
    delay = 5

    def __init__(self, name, owner, inputs=2):
        Circuit.__init__(self, name, owner)
        for i in range(inputs):
            Plug(True, None, self)
        Plug(False, None, self)
        self.init_inputs()

    def evalfun(self):
        val = not all([inp.value for inp in self.inputList])
        for inp in self.inputList:
            if inp.value is None and not val:
                val = None
        agenda_.schedule(self, lambda: self.outputList[0].set(val))


class OrGate(Circuit):
    """Any number of inputs. Output true unless every input false."""
    delay = 5

    def __init__(self, name, owner, inputs=2):
        Circuit.__init__(self, name, owner)
        for i in range(inputs):
            Plug(True, None, self)
        Plug(False, None, self)
        self.init_inputs()

    def evalfun(self):
        val = any([inp.value for inp in self.inputList])
        for inp in self.inputList:
            if inp.value is None and not val:
                val = None
        agenda_.schedule(self, lambda: self.outputList[0].set(val))


class NorGate(Circuit):
    """Any number of inputs. Output false unless every input false."""
    delay = 7

    def __init__(self, name, owner, inputs=2):
        Circuit.__init__(self, name, owner)
        for i in range(inputs):
            Plug(True, None, self)
        Plug(False, None, self)
        self.init_inputs()

    def evalfun(self):
        val = not any([inp.value for inp in self.inputList])
        for inp in self.inputList:
            if inp.value is None and not val:
                val = None
        agenda_.schedule(self, lambda: self.outputList[0].set(val))


class XorGate(Circuit):
    delay = 15

    def __init__(self, name, owner, inputs=2):
        Circuit.__init__(self, name, owner)
        for i in range(inputs):
            Plug(True, None, self)
        Plug(False, None, self)
        self.init_inputs()

    def evalfun(self):
        valuesList = [input.value for input in self.inputList]
        val = valuesList.count(True) % 2
        for inp in self.inputList:
            if inp is None:
                val = None
        agenda_.schedule(self, lambda: self.outputList[0].set(val))


class XnorGate(Circuit):
    delay = 15

    def __init__(self, name, owner, inputs=2):
        Circuit.__init__(self, name, owner)
        for i in range(inputs):
            Plug(True, None, self)
        Plug(False, None, self)
        self.init_inputs()

    def evalfun(self):
        valuesList = [inp.value for inp in self.inputList]
        val = all(valuesList) or not any(valuesList)
        for inp in self.inputList:
            if inp is None and val:
                val = None
        agenda_.schedule(self, lambda: self.outputList[0].set(val))
