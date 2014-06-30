#####################################################
## circuits avancés prédéfinies construit à partir ##
##     de portes logiques et d'autres circuits     ##
#####################################################

from comod import _INPUT
from comod import _OUTPUT
from simulator import *
from gates import *


# demi-additionneur: calcule la somme S avec retenue C de A et B
class HalfAdder(Circuit):
    def __init__(self, name):
        Circuit.__init__(self, name)
        # entrées du circuit
        self.A = self.add_input('A', False)    # inputList[0]
        self.B = self.add_input('B', False)    # inputList[1]
        # sorties du circuit
        self.S = self.add_output('S', False)   # outputList[0]
        self.O = self.add_output('O', False)   # outputList[1]
        # composantes du circuit
        self.XOR1 = self.add_circuit(XorGate('X1'))
        self.AND1 = self.add_circuit(AndGate('A1'))
        # connexions des composantes du circuit
        self.A.connect([self.XOR1.inputList[0], self.AND1.inputList[0]])
        self.B.connect([self.XOR1.inputList[1], self.AND1.inputList[1]])
        self.XOR1.outputList[0].connect(self.outputList[0])
        self.AND1.outputList[0].connect(self.outputList[1])


# additionneur complet: calcule la somme S et retenue Cout de A et B et Cin
class FullAdder(Circuit):
    def __init__(self, name):
        Circuit.__init__(self, name)
        # entrées du circuit
        self.A = self.add_input('A')
        self.B = self.add_input('B')
        self.Cin = self.add_input('Cin')
        # sorties du circuit
        self.S = self.add_output('S')
        self.Cout = self.add_output('Cout')
        # composantes du circuit
        self.HA1 = HalfAdder('HA1')
        self.HA2 = HalfAdder('HA2')
        self.OR1 = OrGate('OR1')
        # connexions des composantes du circuit
        self.A.connect([self.HA1.inputList[0]])
        self.B.connect([self.HA1.inputList[1]])
        self.Cin.connect([self.HA2.inputList[0]])
        self.HA1.outputList[0].connect([self.HA2.inputList[1]])
        self.HA1.outputList[1].connect([self.OR1.inputList[1]])
        self.HA2.outputList[1].connect([self.OR1.inputList[0]])
        self.HA2.outputList[0].connect([self.outputList[0]])
        self.OR1.outputList[0].connect([self.outputList[1]])


# bascule RS: permet de positionner la sortie Q à 1 (Set) ou à 0 (Reset)
class RSFlipflop(Circuit):
    def __init__(self, name):
        Circuit.__init__(self, name)
        self.S = Input('S', self, False)  # i: bitS
        self.R = Input('R', self, False)  # i: bitQ
        self.Q = Output('Q', self, True)  # o: 1 si ~S OU 0 si ~R
        # composantes du circuit
        self.N1 = NandGate('N1', self)
        self.N2 = NandGate('N2', self)
        # connexions des composantes du circuit
        self.S.connect([self.N1.A])
        self.R.connect([self.N2.B])
        self.N1.O.connect([self.N2.A, self.Q])
        self.N2.O.connect([self.N1.B])


# bascule D: permet de mémoriser l'entrée D à chaque tic d'horloge C
class DFlipFlop(Circuit):
    def __init__(self, name):
        Circuit.__init__(self, name)
        self.D = Input('D', self, False)   # i: bitD
        self.C = Input('C', self, False)   # i: Clock
        self.Q = Output('Q', self, False)  # o: bit mémorisé
        # composantes du circuit
        self.NA0 = NandGate('NA0', self)
        self.NA1 = NandGate('NA1', self)
        self.NA2 = NandGate('NA2', self)
        self.NA3 = NandGate('NA3', self)
        # connexions des composantes du circuit
        self.D.connect([self.NA0.A])
        self.C.connect([self.NA1.B, self.NA0.B])
        self.NA0.O.connect([self.NA1.A, self.NA2.A])
        self.NA1.O.connect([self.NA3.B])
        self.NA2.O.connecth([self.NA3.A, self.Q])
        self.NA3.O.connect([self.NA2.B])


class DFlipFlopMasterSlave(Circuit):
    def __init__(self, name):
        Circuit.__init__(self, name)
        self.D = Input('D', self, False)   # i: bitD
        self.C = Input('C', self, False)   # i: Clock
        self.Q = Output('Q', self, False)  # o: bit à mémoriser
        # composantes du circuit
        self.DFF0 = DFlipFlop('DFF0', self)
        self.DFF1 = DFlipFlop('DFF1', self)
        self.NOT0 = NotGate('NOT0', self)
        # connexions des composantes du circuit
        self.D.connect([self.DFF0.D])
        self.C.connect([self.DFF0.C, self.NOT0.A])
        self.NOT0.O.connect([self.DFF1.C])
        self.DFF0.Q.connect([self.DFF1.D])
        self.DFF1.Q.connect([self.Q])


class TwoTwoMemory(Circuit):
    def __init__(self, name):
        Circuit.__init__(self, name)
        self.S = Input('A', self, False)     # i: sélecteur
        self.RW = Input('RW', self, False)   # i: 0: read, 1: write
        self.D0 = Input('D0', self, False)   # i: bitD0
        self.D1 = Input('D1', self, False)   # i: bitD1
        self.O0 = Output('O0', self, False)  # o: sortie registre0
        self.O1 = Output('O1', self, False)  # o: sortie registre1
        # composantes du circuit
        self.AN0 = AndGate('AN0', self)
        self.AN1 = AndGate('AN1', self)
        self.AN2 = AndGate('AN2', self)
        self.AN3 = AndGate('AN3', self)
        self.AN4 = AndGate('AN4', self)
        self.AN5 = AndGate('AN5', self)
        self.AN6 = AndGate('AN6', self)
        self.AN7 = AndGate('AN7', self)
        self.NO0 = NotGate('NO0', self)
        self.NO1 = NotGate('NO1', self)
        self.OR0 = OrGate('OR0', self)
        self.OR1 = OrGate('OR1', self)
        self.DFF0 = DFlipFlop('DFF0', self)
        self.DFF1 = DFlipFlop('DFF1', self)
        self.DFF2 = DFlipFlop('DFF2', self)
        self.DFF3 = DFlipFlop('DFF3', self)
        # connexions des composantes du circuit
        self.S.connect([self.NO0.A, self.AN1.A, self.AN2.A, self.AN3.A])
        self.RW.connect([self.AN0.B, self.NO1.A, self.AN1.B])
        self.D0.connect([self.DFF0.D, self.DFF2.D])
        self.D1.connect([self.DFF1.D, self.DFF3.D])
        self.NO0.O.connect([self.AN0.A, self.AN4.A, self.AN5.A])
        self.NO1.B.connect([self.AN7.A, self.AN6.A])
        self.AN0.O.connect([self.DFF2.C, self.DFF3.C])
        self.AN1.O.connect([self.DFF0.C, self.DFF1.C])
        self.AN2.O.connect([self.OR0.A])
        self.AN3.O.connect([self.OR1.A])
        self.AN4.O.connect([self.OR0.B])
        self.AN5.O.connect([self.OR1.B])
        self.AN6.O.connect([self.O1])            # output O0
        self.AN7.O.connect([self.O0])            # output O1
        self.OR0.O.connect([self.AN7.B])
        self.OR1.O.connect([self.AN6.B])
        self.DFF0.Q.connect([self.AN2.B])
        self.DFF1.Q.connect([self.AN3.B])
        self.DFF2.Q.connect([self.AN4.B])
        self.DFF3.Q.connect([self.AN5.B])


class FourOneMux(Circuit):
    def __init__(self, name):
        Circuit.__init__(self, name)
        self.I0 = Input('I0', self, False)
        self.I1 = Input('I1', self, False)
        self.I2 = Input('I2', self, False)
        self.I3 = Input('I3', self, False)
        self.S0 = Input('S0', self, False)
        self.S1 = Input('S1', self, False)
        self.O0 = Output('O0', self, False)
        # composantes du circuit
        self.AN30 = AndGateThree(self, 'AN30')
        self.AN31 = AndGateThree(self, 'AN31')
        self.AN32 = AndGateThree(self, 'AN32')
        self.AN33 = AndGateThree(self, 'AN33')
        self.NOT0 = NotGate('NOT0', self)
        self.NOT1 = NotGate(self, 'NOT1')
        self.OR40 = OrGateFour(self, 'OR40')
        # connexions des composantes du circuit
        self.I0.connect([self.AN30.A])
        self.I1.connect([self.AN31.A])
        self.I2.connect([self.AN32.A])
        self.I3.connect([self.AN33.A])
        self.S0.connect([self.NOT1.A, self.AN31.C, self.AN33.C])
        self.S1.connect([self.NOT0.A, self.AN32.B, self.AN33.B])
        self.NOT0.O.connect([self.AN30.B, self.AN31.B])
        self.NOT1.B.connect([self.AN30.C, self.AN32.C])
        self.AN30.D.connect([self.OR40.A])
        self.AN31.D.connect([self.OR40.B])
        self.AN32.D.connect([self.OR40.C])
        self.AN33.D.connect([self.OR40.D])
        self.OR40.E.connect([self.O0])
