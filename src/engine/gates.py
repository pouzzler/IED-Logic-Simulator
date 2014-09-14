#!/usr/bin/env python3
# coding: utf-8

"""Builtin gates. Unlike user circuits, their evalfun() is implemented."""

from .simulator import *


class NotGate(Circuit):
    """One input only. Output == not Input."""
    
    def __init__(self, name, owner, category=None):
        Circuit.__init__(self, name, owner)
        Plug(True, None, self)
        Plug(False, None, self)

    def evalfun(self):
        self.outputList[0].set(not self.inputList[0].value)


class AndGate(Circuit):
    """Any number of inputs. Output false unless every input true."""
    
    def __init__(self, name, owner, inputs=2):
        Circuit.__init__(self, name, owner)
        for i in range(inputs):
            Plug(True, None, self)
        Plug(False, None, self)

    def evalfun(self):
        self.outputList[0].set(all([inp.value for inp in self.inputList]))


class OrGate(Circuit):
    """Any number of inputs. Output true unless every input false."""
    
    def __init__(self, name, owner, inputs=2):
        Circuit.__init__(self, name, owner)
        for i in range(inputs):
            Plug(True, None, self)
        Plug(False, None, self)

    def evalfun(self):
        self.outputList[0].set(any([inp.value for inp in self.inputList]))


class NorGate(Circuit):
    """Any number of inputs. Output false unless every input false."""

    def __init__(self, name, owner, inputs=2):
        Circuit.__init__(self, name, owner)
        for i in range(inputs):
            Plug(True, None, self)
        Plug(False, None, self)

    def evalfun(self):
        self.outputList[0].set(not any([inp.value for inp in self.inputList]))


class XorGate(Circuit):
    def __init__(self, name, owner, inputs=2):
        Circuit.__init__(self, name, owner)
        for i in range(inputs):
            Plug(True, None, self)
        Plug(False, None, self)

    def evalfun(self):
        valuesList = [input.value for input in self.inputList]
        self.outputList[0].set(valuesList.count(1) % 2)


class XnorGate(Circuit):
    def __init__(self, name, owner, inputs=2):
        Circuit.__init__(self, name, owner)
        for i in range(inputs):
            Plug(True, None, self)
        Plug(False, None, self)

    def evalfun(self):
        valuesList = [inp.value for inp in self.inputList]
        self.outputList[0].set(all(valuesList) or not any(valuesList))


class NandGate(Circuit):
    """Any number of inputs. Output true unless every input true."""
    
    def __init__(self, name, owner, inputs=2):
        Circuit.__init__(self, name, owner)
        for i in range(inputs):
            Plug(True, None, self)
        Plug(False, None, self)

    def evalfun(self):
        out = False
        for inp in self.inputList:
            if inp.value is False:
                out = True
                break
        self.outputList[0].set(out)
