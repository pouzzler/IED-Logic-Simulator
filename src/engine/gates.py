#!/usr/bin/env python3
# coding: utf-8

"""
############################################################
##                  basic logic gates                     ##
##  these gates allow you to build more complex circuits  ##
##           circuits.py contains some examples           ##
##   user_circuits contains those defined by the user     ##
############################################################

These classes represent the basic logic gates.
Unlike sequential circits they have an evalfun() function
which allows to calculate their output based on their inputs.
The names of these classes are the name of the door + 'Gate',
according to the naming convention of pep8.

Note: Only NOT, AND and OR gates can't be created as sequential circuits.
"""

from .simulator import *


# NOT gate
class NotGate(Circuit):
    def __init__(self, owner, name=None):
        Circuit.__init__(self, owner, name)
        self.add_input()
        self.add_output()

    def evalfun(self):
        self.outputList[0].set(not self.inputList[0].value)


# AND gate
class AndGate(Circuit):
    def __init__(self, owner, name=None, inputs=2):
        Circuit.__init__(self, owner, name)
        for inp in range(inputs):
            self.add_input()
        self.add_output()

    def evalfun(self):
        self.outputList[0].set(all([inp.value for inp in self.inputList]))


# OR gate
class OrGate(Circuit):
    def __init__(self, owner, name=None, inputs=2):
        Circuit.__init__(self, owner, name)
        for inp in range(inputs):
            self.add_input()
        self.add_output()

    def evalfun(self):
        self.outputList[0].set(any([inp.value for inp in self.inputList]))


# NOR gate
class NorGate(Circuit):
    def __init__(self, owner, name=None, inputs=2):
        Circuit.__init__(self, owner, name)
        for inp in range(inputs):
            self.add_input()
        self.add_output()

    def evalfun(self):
        self.outputList[0].set(not any([inp.value for inp in self.inputList]))


# XOR gate
class XorGate(Circuit):
    def __init__(self, owner, name=None, inputs=2):
        Circuit.__init__(self, owner, name)
        for inp in range(inputs):
            self.add_input()
        self.add_output()

    def evalfun(self):
        c = 0
        for inp in self.inputList:
            if inp.value is True:
                c += 1
        self.outputList[0].set(c % 2)


# XNOR gate
class XnorGate(Circuit):
    def __init__(self, owner, name=None, inputs=2):
        Circuit.__init__(self, owner, name)
        for inp in range(inputs):
            self.add_input()
        self.add_output()

    def evalfun(self):
        valuesList = [inp.value for inp in self.inputList]
        self.outputList[0].set(all(valuesList) or not any(valuesList))


# NAND gate
class NandGate(Circuit):
    def __init__(self, owner, name=None, inputs=2):
        Circuit.__init__(self, owner, name)
        for inp in range(inputs):
            self.add_input()
        self.add_output()

    def evalfun(self):
        out = False
        for inp in self.inputList:
            if inp.value is False:
                out = True
                break
        self.outputList[0].set(out)
