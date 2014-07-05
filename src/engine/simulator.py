#!/usr/bin/env python3
# coding: utf-8

"""
########################################
## Simulates circuits and logic gates ##
########################################

A circuit (circuit class) includes a set of connectors (Plug class) that
can be inputs or outputs and a set of sub-circuits (Circuit class).
Inputs, outputs and sub-circuits of a circuit are stored in inInputList,
outputlist and circuitList lists, respectively.
Plugs and Circuits may have an optional name.

There are two ways to access a component (Plug or Circuit) of a circuit:
* Using its index in the list: circuit.inputList ([1])
* Using its name (if any): circuit.input ('B')

When the value (Boolean) of an input is modified (with .set()), the entire
circuit is evaluated: all outputs are recalculated based on the values ​​of
its inputs and connections between components.
"""

import logging

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class Plug:
    """Represents an input or output."""

    def __init__(self, isInput, name, owner):
        self.owner = owner        # circuit or door featuring this I/O
        self.name = name          # its name
        self.isInput = isInput    # specifies whether to evaluate the values
        self.value = False        # at first, no electricity
        self.nbEval = 0           # number of evaluations
        self.connections = []     # connected plugs list

    def set(self, value):
        """Sets the boolean value of a Plug."""
        if self.value == value and self.nbEval != 0:  # unchanged value, stop!
            return
        else:                               # else, set the new value
            self.value = bool(value)
            self.nbEval += 1
        log.info(
            '%s.%s set to %i'
            % (self.owner.name, self.name, int(self.value),))
        if self.isInput:                    # input? evaluate the circuit
            self.owner.evalfun()
        for connection in self.connections:
            connection.set(value)           # set value of the connected plugs

    def connect(self, plugList, verbose=True):
        """Connects a Plug to a list of Plugs."""
        if not isinstance(plugList, list):
            plugList = [plugList]           # create a list
        for plug in plugList:
            self.connections.append(plug)   # add each connection of the lists
            if verbose:
                log.info(
                    '%s %s.%s connected to %s %s.%s'
                    % (
                        'input' if plug.isInput else 'output',
                        plug.owner.name,
                        plug.name,
                        'input' if self.isInput else 'output',
                        self.owner.name, self.name,))


class Circuit:
    """Represents a logic circuit."""
    
    def __init__(self, name):
        self.name = name        # name (optional)
        self.inputList = []     # circuit's inputs list
        self.outputList = []    # circuit's outputs list
        self.circuitList = []   # circuit's circuits list
        log.info("%s '%s' has been created" % (self.class_name(), self.name,))

    def add_plug(self, plug):
        """Add a plug (input or output) in the appropriate list of the circuit.
        """
        if plug.isInput:
            self.inputList.append(plug)
            log.info("input '%s' added to %s" % (plug.name, self.name,))
        else:
            self.outputList.append(plug)
            log.info("output '%s' added to %s" % (plug.name, self.name,))

    def add_input(self, name=None):
        """Add an input to the inputList of the circuit."""
        self.inputList.append(Plug(True, name, self))
        log.info("input '%s' added to %s" % (name, self.name,))
        return self.inputList[-1]

    def add_output(self, name=None):
        """Add an output to the outputList of the circuit."""
        self.outputList.append(Plug(False, name, self))
        log.info("output '%s' added to %s" % (name, self.name,))
        return self.outputList[-1]

    def add_circuit(self, circuit):
        """Add an circuit to the circuitList of the circuit."""
        self.circuitList.append(circuit)
        log.info(
            "circuit %s '%s' added to %s"
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


#        -+-------------------- OBJECTS COUNTER --------------------+-        #
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


def total_nb_inputs(circuits):
    """Total number of inputs used in a list of circuits."""
    return count_items(circuits, 'nb_inputs')


def total_nb_outputs(circuits):
    """Total number of outputs used in a list of circuits."""
    return count_items(circuits, 'nb_outputs')


def total_nb_plugs(circuits):
    """Total number of I/O used in a list of circuits."""
    return count_items(circuits, 'nb_plugs')


def total_nb_circuits(circuits):
    """Total number of circuits used (including sub-circuits)
    in a list of circuits.
    """
    return count_items(circuits, 'nb_circuits') + 1  # + top-level circuit
