#!/usr/bin/env python3
# coding: utf-8

"""
#############################################################
## tries to simulate circuits and logic gates using python ##
#############################################################

A circuit (circuit class) includes a set of connectors (Plug class) that
can be inputs or outputs and a set of sub-circuits (Circuit class).
Inputs, outputs and sub-circuits of a circuit are stored in inInputList,
outputlist and circuitList lists, respectively.
Plugs and Circuits can have a name but it's optional.

There are two ways to access a component (Plug or Circuit) of a circuit:
* Using its index in the list: circuit.inputList ([1])
* Using its name (if any): circuit.input ('B')

When the value (Boolean) of an input is modified (with .set()), the entire
circuit is evaluated: all outputs are recalculated based on the values ​​of
its inputs and connections between components.
"""

import logging
from log.log import Log


#============================== SIMULATOR ENGINE =============================#
#        -+------------------------ CLASSES ------------------------+-        #
class Plug:
    """The Plug class: a plug is an input or an output."""
    def __init__(self, isInput, name, owner):
        self.owner = owner        # circuit or door featuring this I/O
        self.name = name          # its name
        self.isInput = isInput    # specifies whether to evaluate the values
        self.value = False        # at first, no electricity
        self.nbEval = 0           # number of evaluations
        self.connections = []     # connected plugs list

    def set(self, value):
        """Set the value of a plug
        usage: plug.set([0/1])
        """
        if self.value == value and self.nbEval != 0:  # unchanged value, stop!
            return
        else:                               # else, set the new value
            self.value = bool(value)
            self.nbEval += 1
        if self.isInput:                    # input? evaluate the circuit
            self.owner.evalfun()
        TopLevel.log.print_message(
            '    # %s.%s set to %i'
            % (self.owner.name, self.name, int(self.value)))
        for connection in self.connections:
            connection.set(value)           # set value of the connected plugs

    def connect(self, plugList, verbose=True):
        """Add one or multiple connexions between a single object and others
        usage: plugE.connect([plugA, plugB, ..., plugN]) / plugE.connect(plugA)
        """
        if not isinstance(plugList, list):
            plugList = [plugList]           # create a list
        for plug in plugList:
            self.connections.append(plug)   # add each connection of the lists
            if verbose:
                TopLevel.log.print_message(
                    '    ~ Plug %s.%s connected to Plug %s.%s'
                    % (plug.owner.name, plug.name, self.owner.name, self.name))


class Circuit:
    """ The Circuit class for the logic circuits and gates."""
    def __init__(self, name):
        self.name = name        # name (optional)
        self.inputList = []     # circuit's inputs list
        self.outputList = []    # circuit's outputs list
        self.circuitList = []   # circuit's circuits list
        TopLevel.log.print_message(
            "> %s '%s' has been created"
            % (self.class_name(), self.name,))

    def add_plug(self, plug):
        """Add a plug (input or output) in the appropriate list of the circuit.
        """
        if plug.isInput:
            self.inputList.append(plug)
            TopLevel.log.print_message(
                "    + plug '%s' add to %s.inputList"
                % (plug.name, self.name,))
        else:
            self.outputList.append(plug)
            TopLevel.log.print_message(
                "    + plug '%s' add to %s.outputList"
                % (plug.name, self.name,))

    def add_input(self, name=None):
        """Add an input to the inputList of the circuit."""
        self.inputList.append(Plug(True, name, self))
        TopLevel.log.print_message(
            "    + plug '%s' add to %s.inputList"
            % (name, self.name,))
        return self.inputList[-1]

    def add_output(self, name=None):
        """Add an output to the outputList of the circuit."""
        self.outputList.append(Plug(False, name, self))
        TopLevel.log.print_message(
            "    + plug '%s' add to %s.outputList"
            % (name, self.name,))
        return self.outputList[-1]

    def add_circuit(self, circuit):
        """Add an circuit to the circuitList of the circuit."""
        self.circuitList.append(circuit)
        TopLevel.log.print_message(
            "  + circuit %s '%s' add to %s.circuitsList"
            % (circuit.class_name(), circuit.name, self.name,))
        return self.circuitList[-1]

    def class_name(self):
        """Return the original clas name of the circuit instance."""
        return self.__class__.__name__

    def input(self, inputName):
        """Returns the input of the circuit whose name is inputName."""
        for input in self.inputList:
            if input.name == inputName:
                return input

    def output(self, outputName):
        """Returns the output of the circuit whose name is outputName."""
        for output in self.outputList:
            if output.name == outputName:
                return output

    def circuit(self, circuitName):
        """Returns the circuit of the circuit whose name is circuitName."""
        for cicuit in self.circuitList:
            if cicuit.name == circuitName:
                return cicuit

    def nb_inputs(self):
        """Returns the number of inputs of the circuit."""
        return len(self.inputList)

    def nb_outputs(self):
        """Returns the number of outputs of the circuit."""
        return len(self.outputList)

    def nb_plugs(self):
        """Returns the number of I/O of the circuit."""
        return self.nb_inputs() + self.nb_outputs()

    def nb_circuits(self):
        """Returns the number of sub-circuits of the circuit."""
        return len(self.circuitList)

    def evalfun(self):
        """Only child classes can have an evalfun."""
        return


#        -+----------------------- UTILITIES -----------------------+-        #
def print_components(circuit, verbose=True, indent=''):
    """Print the plugs of a circuit and its sub-circuitss."""
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
#        -+-------------------- TOP-LEVEL CLASS --------------------+-        #
class TopLevel:
    """This is a top-level circuit which will contain I/O and sub-circuits.
    it correspond to the drawing area of the gui which contains I/O and
    circuits (especially logic gates) so we can consider itself as a
    standalone circuit.
    """
    # at first the top-level circuit dosen't exist
    # it is a class variable so each instance of this class will inherit it
    TC = None
    # automaticaly create a log manager
    log = Log('simulator.log', logging.DEBUG, logfile=True, terminal=True)

    # the circuit is initialized when the class is instantiated for first time
    def __init__(self, name):
        TopLevel.TC = Circuit(name)


#        -+--------------- ADD OBJETCS TO TOP-LEVEL ----------------+-        #
def add_plug(plug):
    """Add an I/O to the list of I/O of the "top-level" circuit."""
    return TopLevel.TC.add_plug(plug)


def add_input(name=None):
    """Add an input to the list of inputs of the "top-level" circuit."""
    return TopLevel.TC.add_input(name)


def add_output(name=None):
    """Add an output to the list of outputs of the "top-level" circuit."""
    return TopLevel.TC.add_output(name)


def add_circuit(name=None):
    """Add a circuit to the list of circuits of the "top-level" circuit."""
    return TopLevel.TC.add_circuit(name)


#        -+-------- ACCESS TOP-LEVEL OBJECTS BY THEIR NAME ---------+-        #
def input(inputName):
    """Returns the input of the "top-level" circuit whose name is inputName.
        /!\ Override la fonction input de python 3.
    """
    return TopLevel.TC.input(inputName)


def output(outputName):
    """Returns the output of the "top-level"
    circuit whose name is outputName.
    """
    return TopLevel.TC.input(outputName)


def circuit(circuitName):
    """Returns the circuit of the "top-level"
    circuit whose name is circuitName.
    """
    return TopLevel.TC.input(circuitName)


#        -+--------------- TOP-LEVEL OBJECTS COUNTER ---------------+-        #
def count_items(circList, method):
    """Calculates the number of inputs,
    outputs or circuits in a list of circuits.
    """
    if not isinstance(circList, list):
        circList = [circList]
    c = 0
    for circuit in circList:
        c += eval('circuit.%s()' % (method,))\
            + count_items(circuit.circuitList, method)
    return c


def total_nb_inputs():
    """Total number of inputs used."""
    return count_items(TopLevel.TC, 'nb_inputs')


def total_nb_outputs():
    """Total number of outputs used."""
    return count_items(TopLevel.TC, 'nb_outputs')


def total_nb_plugs():
    """Total number of I/O used."""
    return count_items(TopLevel.TC, 'nb_plugs')


def total_nb_circuits():
    """Total number of circuits used (including sub-circuits)."""
    return count_items(TopLevel.TC, 'nb_circuits') + 1  # + top-level circuit
