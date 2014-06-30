####################################################################
##              portes logiques de base: NON, OU, ET              ##
## ces portes permettent de sontruire des circuits plus complexes ##
##             circuits.py contient quelques exemples             ##
##      user_circuits contient ceux définis par l'utilisateur     ##
####################################################################

from comod import _INPUT
from comod import _OUTPUT
from simulator import *


# porte NOT
class NotGate(Circuit):
    def __init__(self, name=None):
        Circuit.__init__(self, name)
        self.A = Input('I', self, False)
        self.add_output('O', False)

    def evalfun(self):
        self.outputList[0].set(not self.A.value)


# porte AND
class AndGate(Circuit):
    def __init__(self, name=None, inputs=2):
        Circuit.__init__(self, name)
        for inp in range(inputs):         # ajoute les entrées à la liste
            self.add_input('I' + str(inp), False)
        self.add_output('O', False)

    def evalfun(self):                    # ET logique de toutes les entrées
        out = True
        for inp in self.inputList:
            if inp.value is False:
                out = False
                break
        self.outputList[0].set(out)


# porte OR
class OrGate(Circuit):
    def __init__(self, name=None, inputs=2):
        Circuit.__init__(self, name)
        for inp in range(inputs):
            self.add_input('I' + str(inp), False)
        self.add_output('O', False)

    def evalfun(self):
        out = False
        for inp in self.inputList:
            if inp.value is True:
                out = True
                break
        self.outputList[0].set(out)


# porte XOR
class XorGate(Circuit):
    def __init__(self, name, inputs=2):
        Circuit.__init__(self, name)
        for inp in range(inputs):
            self.add_input('I' + str(inp), False)
        self.add_output('O', False)

    def evalfun(self):
        c = 0
        for inp in self.inputList:
            if inp.value is True:
                c += 1
        self.outputList[0].set(c % 2)


# porte NAND
class NandGate(Circuit):
    def __init__(self, name, inputs=2):
        Circuit.__init__(self, name)
        for inp in range(inputs):
            self.add_input('I' + str(inp), False)
        self.add_output('O', False)

    def evalfun(self):
        out = False
        for inp in self.inputList:
            if inp.value is False:
                out = True
                break
        self.outputList[0].set(out)
