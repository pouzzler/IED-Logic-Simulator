#!/usr/bin/env python
# coding=utf-8
 

class Circuit():
    """Represents a logical circuit"""
    def __init__(self, nInputs, nOutputs):
        self.inputs = [None for i in range(nInputs)]
        self.outputs = [[None, {}] for i in range(nOutputs)]

    def connect(self, outputIndex, circuit, inputIndex):
        self.outputs[outputIndex][1].setdefault(circuit, []).append(inputIndex)

    def set_input(self, index, value):
        if value != self.inputs[index]:
            self.inputs[index] = value
            self.eval_circuit()
    
    def eval_circuit():
        

c1 = Circuit(2, 1)
c2 = Circuit(1, 1)


lorsqu'une entrée est modifiée :
    le circuit doit se réévaluer
    
    soit c'est une porte de base, la réévaluation se fait par une fonction
    
    soit c'est un circuit complexe, la réévaluation se fait en propageant
    la valeur modifiée à des sous-circuits
