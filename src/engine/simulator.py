#!/usr/bin/env python3
# coding: utf-8

#############################################################
## tries to simulate circuits and logic gates using python ##
#############################################################

from .comod import _INPUT, _OUTPUT, _CIRCUIT


#============================== SIMULATOR ENGINE =============================#
#        -+------------------------ CLASSES ------------------------+-        #
# plug class, a plug is an input or an output
class Plug:
    def __init__(self, ptype, name, owner):
        self.owner = owner        # circuit or door featuring this I/O
        self.name = name          # its name
        self.ptype = ptype        # specifies whether to evaluate the values
        self.value = False        # at first, no electricity
        self.nbEval = 0           # number of evaluations
        self.connections = []     # connected plugs list

    # usage: plug.set([0/1])
    def set(self, value):
        if self.value == value and self.nbEval != 0:  # unchanged value, stop!
            return
        else:                               # else, set the new value
            self.value = bool(value)
            self.nbEval += 1
        if self.ptype is _INPUT:            # input? evaluate the circuit
            self.owner.evalfun()
        for connection in self.connections:
            connection.set(value)           # set value of the connected plugs

    # usage: plugE.connect([plugA, plugB, ..., plugN]) / plugE.connect(plugA)
    def connect(self, plugList, verbose=True):
        if not isinstance(plugList, list):
            plugList = [plugList]           # create a list
        for plug in plugList:
            self.connections.append(plug)   # add each connection of the lists
            if verbose:
                print('    ~ Plug %s connected to Plug %s'
                    % (plug.name, self.name,))


# class for the logic circuits and gates
class Circuit:
    def __init__(self, name):
        self.name = name        # name (optional)
        self.inputList = []     # circuit's inputs list
        self.outputList = []    # circuit's outputs list
        self.circuitList = []   # circuit's circuits list
        print('> %s has been created' % (self.name))

    # add a plug (input or output) in the appropriate list of the circuit
    def add_plug(self, plug):
        if plug.ptype is _INPUT:
            self.inputList.append(plug)
        elif plug.ptype is _OUTPUT:
            self.outputList.append(plug)
        else:
            exit('add_plug: wrong plug type')
        print('    + plug %s add to %s.xxxputList' % (plug.name, self.name,))

    # add an input to the inputList of the circuit
    def add_input(self, name=None):
        self.inputList.append(Plug(_INPUT, name, self))
        print("    + plug '%s' add to %s.inputList" % (name, self.name,))
        return self.inputList[-1]

    # add an output to the outputList of the circuit
    def add_output(self, name=None):
        self.outputList.append(Plug(_OUTPUT, name, self))
        print("    + plug '%s' add to %s.outputList" % (name, self.name,))
        return self.outputList[-1]

    # add an circuit to the circuitList of the circuit
    def add_circuit(self, circuit):
        self.circuitList.append(circuit)
        print("  + circuit %s '%s' add to %s.circuitsList" %
              (circuit.class_name(), circuit.name, self.name,))
        return self.circuitList[-1]

    # return the original clas name of the circuit instance
    def class_name(self):
        return self.__class__.__name__

    # returns the input of the circuit whose name is inputName
    def input(self, inputName):
        for input in self.inputList:
            if input.name == inputName:
                return input

    # returns the output of the circuit whose name is outputName
    def output(self, outputName):
        for output in self.outputList:
            if output.name == outputName:
                return output

    # returns the circuit of the circuit whose name is circuitName
    def circuit(self, circuitName):
        for cicuit in self.circuitList:
            if cicuit.name == circuitName:
                return cicuit

    # returns the number of inputs of the circuit
    def nb_inputs(self):
        return len(self.inputList)

    # returns the number of outputs of the circuit
    def nb_outputs(self):
        return len(self.outputList)

    # returns the number of I/O of the circuit
    def nb_plugs(self):
        return self.nb_inputs() + self.nb_outputs()

    # returns the number of sub-circuits of the circuit
    def nb_circuits(self):
        return len(self.circuitList)

    # only child classes can have an evalfun
    def evalfun(self):
        return


#        -+----------------------- UTILITIES -----------------------+-        #
# print the plugs of a circuit and its sub-circuitss
def print_components(circuit, verbose=True, indent=''):
    if not circuit.name:
        print(indent + '[None]')
    else:
        print(indent + '[' + circuit.class_name, circuit.name + ']')
    for plug in circuit.inputList:
        print(indent + '~~ i\t' + plug.name, end='')
        if verbose:
            print('\tTrue' if plug.value else '\tFalse')
        else:
            print('')
    for plug in circuit.outputList:
        print(indent + '~~ o\t' + plug.name, end='')
        if verbose:
            print('\tTrue' if plug.value else '\tFalse')
        else:
            print('')
    for circuit in circuit.circuitList:
        print_components(circuit, verbose, indent + '~~')


#================================= TOP LEVEL =================================#
#        -+--------------- ADD OBJETCS TO TOP-LEVEL ----------------+-        #
# Add an I/O to the list of I/O of the "top-level" circuit
def add_plug(plug):
    return _TC.add_plug(plug)


# Add an input to the list of inputs of the "top-level" circuit
def add_input(name=None):
    return _TC.add_input(name)


# Add an output to the list of outputs of the "top-level" circuit
def add_output(name=None):
    return _TC.add_output(name)


# Add a circuit to the list of circuits of the "top-level" circuit
def add_circuit(name=None):
    return _TC.add_circuit(name)


#        -+-------- ACCESS TOP-LEVEL OBJECTS BY THEIR NAME ---------+-        #
# returns the input of the "top-level" circuit whose name is inputName
# /!\ override la fonction input de python 3
def input(inputName):
    return _TC.input(inputName)


# returns the output of the "top-level" circuit whose name is outputName
def output(outputName):
    return _TC.input(outputName)


# returns the circuit of the "top-level" circuit whose name is circuitName
def circuit(circuitName):
    return _TC.input(circuitName)


#        -+--------------- TOP-LEVEL OBJECTS COUNTER ---------------+-        #
# calculates the number of inputs, outputs or circuits in a list of circuits
def count_items(circList, items_type):
    if not isinstance(circList, list):
        circList = [circList]
    c = 0
    for circuit in circList:
        if items_type is _INPUT:
            c += circuit.nb_inputs()
        elif items_type is _OUTPUT:
            c += circuit.nb_outputs()
        elif items_type is _INPUT + _OUTPUT:
            c += circuit.nb_plugs()
        elif items_type is _CIRCUIT:
            c += 1
        else:
            exit("count_items: wrong items_type")
        c += count_items(circuit.circuitList, items_type)
    return c


# total number of inputs used
def total_nb_inputs():
    return count_items([_TC], _INPUT)


# total number of outputs used
def total_nb_outputs():
    return count_items([_TC], _OUTPUT)


# total number of I/O used
def total_nb_plugs():
    return count_items([_TC], _INPUT + _OUTPUT)


# total number of circuits used (including sub-circuits)
def total_nb_circuits():
    return count_items([_TC], _CIRCUIT)


#============================== GLOBAL VARIABLES =============================#
# we create a circuit named _TC which will contain I/O and sub-circuits
# it's the top-level circuit wich correspond to the drawing area of the gui
# this area contains I/O and circuits (especially logic gates)
# so we can consider itself as a standalone circuit
_TC = Circuit('TOP_CIRCUIT_0')
