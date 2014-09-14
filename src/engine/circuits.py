#!/usr/bin/env python3
# coding: utf-8


###############################################################################
#         ╔╦╗┌─┐┌─┐┬┌─┐  ╔═╗┬┬─┐┌─┐┬ ┬┬┌┬┐  ╔═╗┬┌┬┐┬ ┬┬  ┌─┐┌┬┐┌─┐┬─┐         #
#         ║║║├─┤│ ┬││    ║  │├┬┘│  │ ││ │   ╚═╗│││││ ││  ├─┤ │ │ │├┬┘         #
#         ╩ ╩┴ ┴└─┘┴└─┘  ╚═╝┴┴└─└─┘└─┘┴ ┴   ╚═╝┴┴ ┴└─┘┴─┘┴ ┴ ┴ └─┘┴└─         #
# -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+- #
#                                                                        2014 #
#                                                           Sébastien MAGNIEN #
#                                                            Mathieu FOURCROY #
# --------------------------------------------------------------------------- #
# Contain some predefined circuits such as adder, memory, register and        #
# flip-flops                                                                  #
# --------------------------------------------------------------------------- #
# TODO: add more circuits                                                     #
###############################################################################


from .simulator import *


class Mem1b(Circuit):
    def __init__(self, name, owner):
        Circuit.__init__(self, name, owner)
        # I/O
        self.ON = Plug(True, 'ON', self)
        self.OFF = Plug(True, 'OFF', self)
        self.Q = Plug(False, 'Q', self)
        # components
        self.NOT = NotGate('NOT', self)
        self.AND = AndGate('AND', self)
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
        Circuit.__init__(self, name, owner)
        self.R = Plug(True, 'R', self)
        self.S = Plug(True, 'S', self)
        self.Q = Plug(False, 'Q', self)
        self.NQ = Plug(False, 'NQ', self)
        self.init_inputs()

    def evalfun(self):
        valQ = None
        valNQ = None
        if self.S.value is False and self.R.value is True:
            valQ = True
            valNQ = not valQ
        if self.S.value is True and self.R.value is False:
            valQ = False
            valNQ = not valQ
        if self.S.value is False and self.R.value is False:
            valQ = None
            valNQ = None
        if self.S.value is True and self.R.value is True:
            valQ = self.Q.value
            valNQ = self.NQ.value
        agenda_.schedule(self, lambda: self.Q.set(valQ))
        agenda_.schedule(self, lambda: self.NQ.set(valNQ))


class DFlipFlop(Circuit):
    def __init__(self, name, owner, category=None):
        Circuit.__init__(self, name, owner)
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
        Circuit.__init__(self, name, owner)
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
        Circuit.__init__(self, name, owner)
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
        Circuit.__init__(self, name, owner)
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
