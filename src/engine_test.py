#!/usr/bin/env python3
# coding: utf-8

#############################################################
## quelques test de construction et simulation de circuits ##
##                sera remplacé par la GUI                 ##
#############################################################

from engine.simulator import log  # le log
from engine.gates import *        # portes logiques de base
from engine.clock import *        # horloge
from os.path import dirname, realpath


HEADER = '\033[95m'
BLUE = '\033[94m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
AUTO = '\033[0m'


def print_plug_info(plug):
    if plug.value is True:
        val = GREEN + 'True' + AUTO
    elif plug.value is False:
        val = RED + 'False' + AUTO
    elif plug.value is None:
        val = YELLOW + 'Unknown' + AUTO
    ownerName = plug.owner.name if plug.owner else 'None'
    print('%s.%s: %s\n\tsourcePlug: %s\n\tdestinationPlugs: %s'
            % (ownerName, plug.name, val,
                str('%s.%s' % (plug.sourcePlug.owner.name, plug.sourcePlug.name) if plug.sourcePlug else ''),
                str(['%s.%s' % (conn.owner.name, conn.name) for conn in plug.destinationPlugs])))


#================================= PROGRAMME =================================#
class oCounter4b(Circuit):
    def __init__(self, name, owner):
        Circuit.__init__(self, name, owner)
        # inputs / outputs
        self.E = Plug(True, 'E', self)
        self.CLK = Plug(True, 'CLK', self)
        self.S0 = Plug(False, 'S0', self)
        self.S1 = Plug(False, 'S1', self)
        self.S2 = Plug(False, 'S2', self)
        self.S3 = Plug(False, 'S3', self)
        # components
        self.JKFF0 = JKFlipFlop('JKFF0', self)
        self.JKFF1 = JKFlipFlop('JKFF1', self)
        self.JKFF2 = JKFlipFlop('JKFF2', self)
        self.JKFF3 = JKFlipFlop('JKFF3', self)
        self.AND0 = AndGate('AND0', self, 3)
        self.AND1 = AndGate('AND1', self)
        # connections
        self.E.connect(self.JKFF0.J)
        self.E.connect(self.JKFF0.K)
        self.CLK.connect(self.JKFF0.CLK)
        self.CLK.connect(self.JKFF1.CLK)
        self.CLK.connect(self.JKFF2.CLK)
        self.CLK.connect(self.JKFF3.CLK)
        self.JKFF0.Q.connect(self.AND0.inputList[0])
        self.JKFF0.Q.connect(self.AND1.inputList[0])
        self.JKFF0.Q.connect(self.JKFF1.J)
        self.JKFF0.Q.connect(self.JKFF1.K)
        self.JKFF1.Q.connect(self.AND0.inputList[1])
        self.JKFF1.Q.connect(self.AND1.inputList[1])
        self.JKFF2.Q.connect(self.AND0.inputList[2])
        self.AND1.outputList[0].connect(self.JKFF2.J)
        self.AND1.outputList[0].connect(self.JKFF2.K)
        self.AND0.outputList[0].connect(self.JKFF3.J)
        self.AND0.outputList[0].connect(self.JKFF3.K)
        self.JKFF0.Q.connect(self.S0)
        self.JKFF1.Q.connect(self.S1)
        self.JKFF2.Q.connect(self.S2)
        self.JKFF3.Q.connect(self.S3)
        

class Counter4b(Circuit):
    def __init__(self, name, owner):
        Circuit.__init__(self, name, owner)
        # inputs / outputs
        self.E = Plug(True, 'E', self)
        self.CLK = Plug(True, 'CLK', self)
        self.S0 = Plug(False, 'S0', self)
        self.S1 = Plug(False, 'S1', self)
        self.S2 = Plug(False, 'S2', self)
        self.S3 = Plug(False, 'S3', self)
        # components
        self.JKFF0 = JKFlipFlop('JKFF0', self)
        self.JKFF1 = JKFlipFlop('JKFF1', self)
        self.JKFF2 = JKFlipFlop('JKFF2', self)
        self.JKFF3 = JKFlipFlop('JKFF3', self)
        self.AND0 = AndGate('AND0', self)
        self.AND1 = AndGate('AND1', self)
        # connections
        self.E.connect(self.JKFF0.J)
        self.E.connect(self.JKFF0.K)
        self.JKFF0.NQ.connect(self.JKFF1.K)
        self.JKFF0.NQ.connect(self.AND0.inputList[1])
        self.JKFF0.NQ.connect(self.JKFF1.J)
        self.JKFF1.NQ.connect(self.AND0.inputList[0])
        self.JKFF1.NQ.connect(self.AND1.inputList[0])
        self.AND0.outputList[0].connect(self.AND1.inputList[1])
        self.AND0.outputList[0].connect(self.JKFF2.K)
        self.AND0.outputList[0].connect(self.JKFF2.J)
        self.AND1.outputList[0].connect(self.JKFF3.K)
        self.AND1.outputList[0].connect(self.JKFF3.J)
        self.CLK.connect(self.JKFF0.CLK)
        self.CLK.connect(self.JKFF1.CLK)
        self.CLK.connect(self.JKFF2.CLK)
        self.CLK.connect(self.JKFF3.CLK)
        self.JKFF0.Q.connect(self.S0)
        self.JKFF1.Q.connect(self.S1)
        self.JKFF2.Q.connect(self.S2)
        self.JKFF3.Q.connect(self.S3)
        

class oJKFlipFlop(Circuit):
    def __init__(self, name, owner):
        Circuit.__init__(self, name, owner)
        # inputs / outputs
        self.J = Plug(True, 'J', self)
        self.K = Plug(True, 'K', self)
        self.CLK = Plug(True, 'CLK', self)
        self.Q = Plug(False, 'Q', self)
        self.NQ = Plug(False, 'NQ', self)
        self.prev = False
        
    def evalfun(self):
        if self.CLK.value and not self.prev:
            if self.J.value and self.K.value:
                q = self.NQ.value
            elif not self.J.value and not self.K.value:
                return
            elif self.J.value and not self.K.value:
                q = 1
            else:
                q = 0
            nq = not q
            self.Q.set(q)
            self.NQ.set(nq)
        self.prev = self.CLK.value
                

class ooJKFlipFlop(Circuit):
    def __init__(self, name, owner):
        Circuit.__init__(self, name, owner)
        # inputs / outputs
        self.J = Plug(True, 'J', self)
        self.K = Plug(True, 'K', self)
        self.CLK = Plug(True, 'CLK', self)
        self.Q = Plug(False, 'Q', self)
        self.NQ = Plug(False, 'NQ', self)
        # components
        self.NA0 = NandGate('NA0', self, 3)
        self.NA1 = NandGate('NA1', self, 3)
        self.NA2 = NandGate('NA2', self)
        self.NA3 = NandGate('NA3', self)
        self.NA4 = NandGate('NA4', self)
        self.NA5 = NandGate('NA5', self)
        self.NA6 = NandGate('NA6', self)
        self.NA7 = NandGate('NA7', self)
        self.NOT = NotGate('NOT', self)
        # connections
        self.J.connect(self.NA0.inputList[0])
        self.K.connect(self.NA1.inputList[2])
        self.CLK.connect(self.NOT.inputList[0])
        self.CLK.connect(self.NA1.inputList[0])
        self.CLK.connect(self.NA0.inputList[2])
        self.NA0.outputList[0].connect(self.NA2.inputList[0])
        self.NA1.outputList[0].connect(self.NA3.inputList[1])
        self.NA2.outputList[0].connect(self.NA3.inputList[0])
        self.NA2.outputList[0].connect(self.NA4.inputList[0])
        self.NA3.outputList[0].connect(self.NA2.inputList[1])
        self.NA3.outputList[0].connect(self.NA5.inputList[1])
        self.NA4.outputList[0].connect(self.NA6.inputList[0])
        self.NA5.outputList[0].connect(self.NA7.inputList[1])
        self.NA6.outputList[0].connect(self.NA1.inputList[1])
        self.NA6.outputList[0].connect(self.Q)
        self.NA6.outputList[0].connect(self.NA7.inputList[0])
        self.NA7.outputList[0].connect(self.NA6.inputList[1])
        self.NA7.outputList[0].connect(self.NA0.inputList[1])
        self.NA7.outputList[0].connect(self.NQ)
        self.NOT.outputList[0].connect(self.NA5.inputList[0])
        self.NOT.outputList[0].connect(self.NA4.inputList[1])
        

class sDFlipFlop(Circuit):
    def __init__(self, name, owner):
        Circuit.__init__(self, name, owner)
        self.D = Plug(True, 'D', self)
        self.CLK = Plug(True, 'CLK', self)
        self.Q = Plug(False, 'Q', self)
        # composantes du circuit
        self.NA0 = NandGate('NA0', self)
        NA0_A = self.NA0.inputList[0]
        NA0_B = self.NA0.inputList[1]
        NA0_O = self.NA0.outputList[0]
        self.NA1 = NandGate('NA1', self)
        NA1_A = self.NA1.inputList[0]
        NA1_B = self.NA1.inputList[1]
        NA1_O = self.NA1.outputList[0]
        self.NA2 = NandGate('NA2', self)
        NA2_A = self.NA2.inputList[0]
        NA2_B = self.NA2.inputList[1]
        NA2_O = self.NA2.outputList[0]
        self.NA3 = NandGate('NA3', self)
        NA3_A = self.NA3.inputList[0]
        NA3_B = self.NA3.inputList[1]
        NA3_O = self.NA3.outputList[0]
        # connexions des composantes du circuit
        self.D.connect(NA0_A)
        NA1_B.connect(self.CLK)
        self.CLK.connect(NA0_B)
        NA0_O.connect(NA1_A)
        NA0_O.connect(NA2_A)
        NA1_O.connect(NA3_B)
        NA2_O.connect(self.Q)
        NA2_O.connect(NA3_A)
        NA3_O.connect(NA2_B)


class Div2(Circuit):
    def __init__(self, name, owner):
        Circuit.__init__ (self, name, owner)
        self.C = Plug(True, 'C', self)
        self.Q = Plug(False, 'Q', self)
        self.Q.value = 0
        #
        self.DFF = DFlipFlop('DFF', self)
        self.NOT = NotGate('NOT', self)
        #
        self.C.connect(self.DFF.CLK)
        self.DFF.Q.connect(self.NOT.inputList[0])
        self.DFF.Q.connect(self.Q)
        self.NOT.outputList[0].connect(self.DFF.D)


################################################################
################################################################
class Mem1b(Circuit):
    def __init__(self, name, owner):
        Circuit.__init__ (self, name, owner)
        # I/O
        self.ON = Plug(True, 'ON', self)
        self.OFF = Plug(True, 'OFF', self)
        self.Q = Plug(False, 'Q', self)
        # components
        self.NOT = NotGate('NOT', self)
        self.AND = NandGate('AND', self)
        self.OR = OrGate('OR', self)
        # connections between components
        self.ON.connect(self.OR.inputList[0])
        self.OFF.connect(self.NOT.inputList[0])
        self.NOT.outputList[0].connect(self.AND.inputList[0])
        self.AND.outputList[0].connect(self.OR.inputList[1])
        self.OR.outputList[0].connect(self.AND.inputList[1])
        self.OR.outputList[0].connect(self.Q)


class RSFlipFlop(Circuit):
    delay = 10
    
    def __init__(self, name, owner, category=None):
        Circuit.__init__ (self, name, owner)
        self.R = Plug(True, 'R', self)
        self.S = Plug(True, 'S', self)
        self.Q = Plug(False, 'Q', self)
        self.NQ = Plug(False, 'NQ', self)
        self.init_inputs()
    
    def evalfun(self):
        valQ = None
        valNQ = None
        if self.S.value == False and self.R.value == True:
            valQ = True
            valNQ = not valQ
        if self.S.value == True and self.R.value == False:
            valQ = False
            valNQ = not valQ
        if self.S.value == False and self.R.value == False:
            valQ = None
            valNQ = None
        if self.S.value == True and self.R.value == True:
            valQ = self.Q.value
            valNQ = self.NQ.value
        agenda_.schedule(self, lambda: self.Q.set(valQ))
        agenda_.schedule(self, lambda: self.NQ.set(valNQ))


class DFlipFlop(Circuit):
    def __init__(self, name, owner, category=None):
        Circuit.__init__ (self, name, owner)
        # I/O
        self.D = Plug(True, 'D', self)
        self.CLK = Plug(True, 'CLK', self)
        self.Q = Plug(False, 'Q', self)
        self.NQ = Plug(False, 'NQ', self)
        self.init_inputs()
        # components
        self.NOT = NotGate('NOT', self)
        self.NAND0 = NandGate('NAND0', self)
        self.NAND1 = NandGate('NAND1', self)
        self.RSFF = RSFlipFlop('RSFF', self)
        # connections between components
        self.D.connect(self.NOT.inputList[0])
        self.D.connect(self.NAND0.inputList[0])
        self.CLK.connect(self.NAND1.inputList[1])
        self.CLK.connect(self.NAND0.inputList[1])
        self.NOT.outputList[0].connect(self.NAND1.inputList[0])
        self.NAND0.outputList[0].connect(self.RSFF.S)
        self.NAND1.outputList[0].connect(self.RSFF.R)
        self.RSFF.Q.connect(self.Q)
        self.RSFF.NQ.connect(self.NQ)


class JKFlipFlop(Circuit):
    delay = 42
    
    def __init__(self, name, owner, category=None):
        Circuit.__init__ (self, name, owner)
        self.J = Plug(True, 'J', self)
        self.K = Plug(True, 'K', self)
        self.CLK = Plug(True, 'CLK', self)
        self.Q = Plug(False, 'Q', self)
        self.NQ = Plug(False, 'NQ', self)
        self.prevClock = False
        self.init_inputs()

    def evalfun(self):
        valQ = self.Q.value
        valNQ = not valQ
        if (not self.CLK.value and self.prevClock and self.J.value is True and
            self.K.value is True):
                #~ print('case 1')
                valQ = not self.Q.value
                valNQ = not valQ
        if self.J.value is False and self.K.value is False:
            #~ print('case 2')
            valQ = self.Q.value
            valNQ = not valQ
        if (self.CLK.value and not self.prevClock and
            self.J.value != self.K.value):
                #~ print('case 3')
                valQ = self.J.value
                valNQ = not valQ
        self.prevClock = self.CLK.value
        agenda_.schedule(self, lambda: self.Q.set(valQ))
        agenda_.schedule(self, lambda: self.NQ.set(valNQ))


class Counter4b(Circuit):
    def __init__(self, name, owner, category=None):
        Circuit.__init__ (self, name, owner)
        # I/O
        self.A = Plug(True, 'A', self)
        self.CLK = Plug(True, 'CLK', self)
        self.Q0 = Plug(False, 'Q0', self)
        self.Q1 = Plug(False, 'Q1', self)
        self.Q2 = Plug(False, 'Q2', self)
        self.Q3 = Plug(False, 'Q3', self)
        self.init_inputs()
        # components
        self.JKFF0 = JKFlipFlop('JKFF0', self)
        self.JKFF1 = JKFlipFlop('JKFF1', self)
        self.JKFF2 = JKFlipFlop('JKFF2', self)
        self.JKFF3 = JKFlipFlop('JKFF3', self)
        self.AND0 = AndGate('AND0', self)
        self.AND1 = AndGate('AND1', self, 3)
        # connections between components
        self.A.connect(self.JKFF0.J)
        self.A.connect(self.JKFF0.K)
        self.CLK.connect(self.JKFF0.CLK)
        self.CLK.connect(self.JKFF1.CLK)
        self.CLK.connect(self.JKFF2.CLK)
        self.CLK.connect(self.JKFF3.CLK)
        self.JKFF0.NQ.connect(self.JKFF1.J)
        self.JKFF0.NQ.connect(self.JKFF1.K)
        self.JKFF0.NQ.connect(self.AND0.inputList[0])
        self.JKFF0.NQ.connect(self.AND1.inputList[0])
        self.JKFF0.Q.connect(self.Q0)
        self.JKFF1.NQ.connect(self.AND0.inputList[1])
        self.JKFF1.NQ.connect(self.AND1.inputList[1])
        self.JKFF1.Q.connect(self.Q1)
        self.JKFF2.NQ.connect(self.AND1.inputList[2])
        self.JKFF2.Q.connect(self.Q2)
        self.JKFF3.Q.connect(self.Q3)
        self.AND0.outputList[0].connect(self.JKFF2.J)
        self.AND0.outputList[0].connect(self.JKFF2.K)
        self.AND1.outputList[0].connect(self.JKFF3.J)
        self.AND1.outputList[0].connect(self.JKFF3.K)


class Register4b(Circuit):
    def __init__(self, name, owner, category=None):
        Circuit.__init__ (self, name, owner)
        # I/O
        self.I0 = Plug(True, 'I0', self)
        self.I1 = Plug(True, 'I1', self)
        self.I2 = Plug(True, 'I2', self)
        self.I3 = Plug(True, 'I3', self)
        self.CLK = Plug(True, 'CLK', self)
        self.Q0 = Plug(False, 'Q0', self)
        self.Q1 = Plug(False, 'Q1', self)
        self.Q2 = Plug(False, 'Q2', self)
        self.Q3 = Plug(False, 'Q3', self)
        # components
        self.DFF0 = DFlipFlop('DFF0', self)
        self.DFF1 = DFlipFlop('DFF1', self)
        self.DFF2 = DFlipFlop('DFF2', self)
        self.DFF3 = DFlipFlop('DFF3', self)
        # connections between components
        self.CLK.connect(self.DFF0.CLK)
        self.CLK.connect(self.DFF1.CLK)
        self.CLK.connect(self.DFF2.CLK)
        self.CLK.connect(self.DFF3.CLK)
        self.I0.connect(self.DFF0.D)
        self.I1.connect(self.DFF1.D)
        self.I2.connect(self.DFF2.D)
        self.I3.connect(self.DFF3.D)
        self.DFF0.Q.connect(self.Q0)
        self.DFF1.Q.connect(self.Q1)
        self.DFF2.Q.connect(self.Q2)
        self.DFF3.Q.connect(self.Q3)


if __name__ == '__main__':
    strFile = (
        dirname(realpath(__file__))
        + '/../lang/strings_' + 'en')
    f = open(strFile, 'r')
    for _, line in enumerate(f):
        if line.startswith('Plug') or line.startswith('Circuit'):
            exec(line)

    # circuit principal
    TC = Circuit("Main_Circuit", None)
    
    MEM = Mem1b('MEM', TC)
    
    #~ R4 = Register4b('                               R4', TC)
    print('===============================')
    #~ R4.I0.set(True)
    #~ R4.I1.set(False)
    #~ R4.I2.set(True)
    #~ R4.I3.set(False)
    #~ print('===============================')
    #~ R4.CLK.set(True)
    #~ R4.CLK.set(False)
    #~ print('===============================')
    
    #~ JKFF = JKFlipFlop('JKFF', TC)
    #~ print('===============================')
    #~ JKFF.J.set(True)
    #~ JKFF.K.set(True)
    #~ print('===============================')
    #~ JKFF.CLK.set(True)
    #~ JKFF.CLK.set(False)
    #~ print('===============================')
    #~ JKFF.CLK.set(True)
    #~ JKFF.CLK.set(False)
    #~ print('===============================')
    #~ JKFF.CLK.set(True)
    #~ JKFF.CLK.set(False)
    #~ print('===============================')
    #~ JKFF.J.set(False)
    #~ print('===============================')
    #~ JKFF.CLK.set(True)
    #~ JKFF.CLK.set(False)
    #~ print('===============================')
    #~ JKFF.CLK.set(True)
    #~ JKFF.CLK.set(False)
    #~ print('===============================')
    #~ print('===============================')
    #~ JKFF.J.set(True)
    #~ JKFF.K.set(False)
    #~ print('===============================')
    #~ JKFF.CLK.set(True)
    #~ JKFF.CLK.set(False)
    #~ print('===============================')

    AND = AndGate('AND', TC)
    A = Plug(True, 'A', TC)
    A.connect(AND.inputList[0])
    A.connect(AND.inputList[1])
    A.set(True)
    

    #~ C4 = Counter4b('                         C4', TC)
    #~ print('===============================')
    #~ C4.A.set(True)
    #~ print('===============================')
    #~ C4.CLK.set(True)
    #~ C4.CLK.set(False)
    #~ print('===============================')
    #~ C4.CLK.set(True)
    #~ C4.CLK.set(False)
    #~ print('===============================')
    #~ C4.CLK.set(True)
    #~ C4.CLK.set(False)
    

    #~ ON = Plug(True, 'ON', TC)
    #~ OFF = Plug(True, 'OFF', TC)
    #~ NOT = NotGate('NOT', TC)
    #~ NAND = NandGate('NAND', TC)
    #~ OR = OrGate('OR', TC)
    #~ ON.connect(OR.inputList[0])
    #~ OFF.connect(NOT.inputList[0])
    #~ NAND.outputList[0].connect(OR.inputList[1])
    #~ OR.outputList[0].connect(NAND.inputList[1])
    #~ NOT.outputList[0].connect(NAND.inputList[0])
    #~ ON.set(True)
    #~ print_plug_info(OR.outputList[0])
    #~ print_plug_info(NAND.outputList[0])
    #~ ON.set(False)
    #~ print_plug_info(OR.outputList[0])
    #~ print_plug_info(NAND.outputList[0])
    #~ OFF.set(True)
    #~ print_plug_info(OR.outputList[0])
    #~ print_plug_info(NAND.outputList[0])

    #~ NAND = NandGate('NAND', TC)
    #~ NAND.inputList[0].set(True)
    #~ NAND.inputList[1].set(None)
    #~ print_plug_info(NAND.outputList[0])


    #~ A = Plug(True, 'A', TC)
    #~ O = Plug(False, 'O', TC)
    #~ NOT = NotGate('Not', TC)
    #~ A.connect(NOT.inputList[0])
    #~ NOT.outputList[0].connect(O)
    #~ A.set(True)
    #~ print_plug_info(A)
    #~ print_plug_info(O)


    #~ MEM = Mem('MEM', TC)
    #~ MEM.OFF.set(0)
    #~ MEM.ON.set(1)
    #~ MEM.ON.set(0)
    #~ print_plug_info(MEM.OR.outputList[0])


    #~ DFF = DFlipFlop("DFF", TC)
    #~ DFF.D.set(1)
    #~ DFF.CLK.set(1)
    #~ DFF.CLK.set(0)
    #~ print_plug_info(DFF.Q)
    #~ DFF.D.set(0)
    #~ DFF.CLK.set(1)
    #~ DFF.CLK.set(0)
    #~ print_plug_info(DFF.Q)


    #~ x = Div2("X", TC)
    #~ c = 0; x.C.set(c)
    #~ while 1 :
        #~ input("Clock is %d. Hit return to toggle clock" % c)
        #~ print(x.DFF.Q.value)
        #~ c = not c
        #~ x.C.set(c)


    #~ JKFF = JKFlipFlop('JKFF', TC)
    #~ JKFF.J.set(True)
    #~ JKFF.K.set(False)
    #~ JKFF.CLK.set(True)
    #~ JKFF.CLK.set(False)
    #~ print_plug_info(JKFF.Q)
    #~ print_plug_info(JKFF.NQ)
    #~ JKFF.K.set(True)
    #~ JKFF.CLK.set(True)
    #~ JKFF.CLK.set(False)
    #~ print_plug_info(JKFF.Q)
    #~ print_plug_info(JKFF.NQ)
    #~ JKFF.CLK.set(True)
    #~ JKFF.CLK.set(False)
    #~ print_plug_info(JKFF.Q)
    #~ print_plug_info(JKFF.NQ)
    #~ 
    #~ C4B = Counter4b('C4B', TC)
    #~ 
    #~ C4B.E.set(True)
    #~ c = 1
    #~ C4B.CLK.set(c)
    #~ while 1:
        #~ input("Clock is %d. Hit return to toggle clock" % c)
        #~ print('%i%i%i%i' % (int(C4B.S3.value), int(C4B.S2.value), int(C4B.S1.value), int(C4B.S0.value)))
        #~ c = not c
        #~ C4B.CLK.set(c)
