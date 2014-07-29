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
* Using its index in the list: circuit.inputList[1]
* Using its name (if any): circuit.input('B')

When the value (Boolean) of an input is modified (with .set()), the entire
circuit is evaluated: all outputs are recalculated based on the values ​​of
its inputs and sourcePlug between components.
"""

# TODO: replace log.error messages by exceptions.
# TODO: add a Circuit.save() method for saving an entire circuit.

import logging


log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
fileHandler = logging.FileHandler('simulator.log')
stdoutHandler = logging.StreamHandler()
fileHandler.setLevel(logging.DEBUG)
stdoutHandler.setLevel(logging.ERROR)
formatter = logging.Formatter(
    '%(asctime)s %(levelname)s %(message)s',
    datefmt='%H:%M:%S')
fileHandler.setFormatter(formatter)
stdoutHandler.setFormatter(formatter)


#============================ CLASS FOR THE PLUGS ============================#
class Plug:
    """Represents an input or output."""

    setInputVerbose = True      # Inputs changes
    setOutputVerbose = True     # Outputs changes
    connectVerbose = True       # Connecting / diconnecting I/O

    def __init__(self, isInput, name, owner):
        self.isInput = isInput    # specifies whether to evaluate the values
        self.owner = owner        # circuit or door featuring this I/O
        if name is None:
            name = self.generate_name()
        self.name = name          # its name
        self.value = False        # at first, no electricity
        self.__nbEval = 0         # number of evaluations
        self.sourcePlug = None     # plug on the left
        self.destinationPlugs = []  # plugs on the right

    def set(self, value):
        """Sets the boolean value of a Plug."""
        if self.value == value and self.__nbEval != 0:  # unchanged value, stop
            return
        else:                           # else, set the new value
            self.value = bool(value)
            self.__nbEval += 1
        if Plug.setInputVerbose and self.isInput:
            log.info(
                'input %s.%s set to %i'
                % (self.owner.name, self.name, int(self.value),))
        if Plug.setOutputVerbose and not self.isInput:
            log.info(
                'output %s.%s set to %i'
                % (self.owner.name, self.name, int(self.value),))
        # if the input of a gate change, we must evaluate its
        # logic function to set its outpu(s) valu(s)
        if self.isInput:
            self.owner.evalfun()
        # then, all plugs in the destination list are set to this value
        for connection in self.destinationPlugs:
            connection.set(value)

    def connect(self, plugList):
        """Connects a Plug to a list of Plugs."""
        if not isinstance(plugList, list):
            plugList = [plugList]           # create a list
        for plug in plugList:
            # INVALID connections:
            #   * connection already exists
            if plug in self.destinationPlugs:
                log.info(
                    'connection between %s and %s already exists'
                    % (self.name, plug.name))
                continue
            #   * I/O => same I/O
            if plug is self:
                log.warning('cannot connect I/O on itself')
                return False
            #   * destination plug already have a source
            if plug.sourcePlug:
                log.warning(
                    '%s.%s already have an incoming connection'
                    % (plug.owner.name, plug.name))
                return False
            # VALID connections:
            srcIsInput = self.isInput
            srcIsOutput = not srcIsInput
            destIsInput = plug.isInput
            destIsOutput = not destIsInput
            srcP = self.owner
            destP = plug.owner
            srcGP = self.owner.owner
            destGP = plug.owner.owner
            print('GP = P: ', srcGP == destP)
            print('srcIsInput: ', srcIsInput)
            print('destIsInput: ', destIsInput)
            #   * Ix => Iy is valid IF Ix.GP != Iy.GP
            #   * Ox => Oy is valid IF Ox.GP != Oy.GP
            #   * O => I is valid IF O.GP == I.GP
            if (srcIsInput and destIsInput and srcGP == destP) or \
                (srcIsOutput and destIsOutput and srcP == destGP):
                    plug.destinationPlugs.append(self)
                    self.sourcePlug = plug
                
            elif (srcIsInput and destIsInput and srcGP != destGP) or \
                (srcIsOutput and destIsOutput and srcGP != destGP) or \
                (srcIsOutput and destIsInput and srcGP == destGP):
                    self.destinationPlugs.append(plug)
                    plug.sourcePlug = self
                

            #  INVALID connections:
            else:
                log.warning(
                    'invalid connection between %s.%s and %s.%s'
                    % (self.owner.name, self.name, plug.owner.name, plug.name))
                return False

            if Plug.connectVerbose:
                log.info(
                    '%s.%s connected to %s.%s'
                    % (self.owner.name, self.name, plug.owner.name,
                    plug.name))

        return True

    def disconnect(self, plug):
        if plug not in self.destinationPlugs and \
            self not in plug.destinationPlugs:
            log.info(
                '%s.%s and %s.%s are not connected'
                 % (self.owner.name, self.name, plug.owner.name, plug.name,))
            return
        elif plug in self.destinationPlugs:
            self.destinationPlugs.remove(plug)
            plug.sourcePlug = None
            plug.set(0)
        else:
            plug.destinationPlugs.remove(self)
            self.sourcePlug = None
            self.set(0)
        log.info(
            '%s.%s and %s.%s disconnected'
            % (self.owner.name, self.name, plug.owner.name, plug.name,))

    def setName(self, name):
        if len(name):
            if (self.isInput and name in [
                    x.name for x in self.owner.inputList]) or \
                    (not self.isInput and name in [
                        x.name for x in self.owner.outputList]):
                log.error('name %s already in use' % (name,))
                return False
            else:
                log.info("%s.%s's name changed to %s" % (
                    self.owner.name, self.name, name,))
                self.name = name
                return True
        else:
            log.error('name must be at least one character long')
            return False

    def generate_name(self):
        """Generate a name for a plug (like 'TOP_INPUT2' or 'OUTPUT1')."""
        i = 0
        names = [io.name for io in (
            self.owner.inputList if self.isInput else self.owner.outputList)]
        while True:
            name = ('INPUT_' if self.isInput else 'OUTPUT_') + str(i)
            if self.owner.owner is None:
                name = 'TOP_' + name
            if name not in names:
                return name
            i += 1


#=========================== CLASS FOR THE CIRCUITS ==========================#
class Circuit:
    """Represents a logic circuit."""

    addPlugVerbose = True         # Adding an I/O
    addCircuitVerbose = True      # Adding a circuit
    removePlugVerbose = True      # Removing an I/O
    removeCircuitVerbose = True   # Removing a circuit
    detailedRemoveVerbose = True  # Detailed remove

    def __init__(self, name, owner):
        self.owner = owner      # parent circuit
        if name is None:
            name = self.generate_name()
        self.name = name        # name (generated if not specified)
        self.inputList = []     # circuit's inputs list
        self.outputList = []    # circuit's outputs list
        self.circuitList = []   # circuit's circuits list
        log.info(
            "circuit %s '%s' has been created"
            % (self.class_name(), self.name,))

    # -+---------------    METHODS FOR ADDING COMPONENTS    ---------------+- #
    def add_plug(self, plug):
        """Add a plug (input or output) in the appropriate list of the circuit.
        """
        if plug.isInput:
            self.inputList.append(plug)
            if Circuit.addPlugVerbose:
                log.info("input '%s' added to %s" % (plug.name, self.name,))
        else:
            self.outputList.append(plug)
            if Circuit.addPlugVerbose:
                log.info("output '%s' added to %s" % (plug.name, self.name,))

    def add_input(self, name=None):
        """Add an input to the inputList of the circuit."""
        input = Plug(True, name, self)
        self.inputList.append(input)
        if Circuit.addPlugVerbose:
            log.info("input '%s' added to %s" % (input.name, self.name,))
        return self.inputList[-1]

    def add_output(self, name=None):
        """Add an output to the outputList of the circuit."""
        output = Plug(False, name, self)
        self.outputList.append(output)
        if Circuit.addPlugVerbose:
            log.info("output '%s' added to %s" % (output.name, self.name,))
        return self.outputList[-1]

    def add_circuit(self, circuitClass, name=None):
        """Add an circuit to the circuitList of the circuit."""
        circuit = circuitClass(name, self)  # also pass inputs using kwargs
        self.circuitList.append(circuit)
        if Circuit.addCircuitVerbose:
            log.info(
                "circuit %s '%s' added to %s"
                % (circuit.class_name(), circuit.name, self.name,))
        return self.circuitList[-1]

    # -+--------------    METHODS FOR REMOVING COMPONENTS    --------------+- #
    # these functions can also be implemented using the component name or
    # index but using its instance is the easiest way
    def remove_input(self, input):
        """Remove an input from the inputList of the circuit."""
        self.inputList.remove(input)
        if Circuit.removePlugVerbose:
            log.info("input '%s' removed from %s" % (input.name, self.name,))

    def remove_output(self, output):
        """Remove an output from the outputList of the circuit."""
        self.outputList.remove(output)
        if Circuit.removePlugVerbose:
            log.info("output '%s' removed from %s" % (output.name, self.name,))

    def __remove_circuit(self, circuit):
        """Remove a circuit from the circuitList of the circuit."""
        self.circuitList.remove(circuit)
        Circuit.removePlugVerbose
        if Circuit.removeCircuitVerbose:
            log.info(
                "circuit %s '%s' removed from %s"
                % (circuit.class_name(), circuit.name, self.name,))

    def remove(self, component):
        """Remove a component (Plug or Circuit) from the circuit."""
        if isinstance(component, Plug):         # it is a Plug
            if component.isInput:               # it is an input Plug
                componentList = self.inputList
                removeMethod = self.__remove_input
            else:                               # it is an output Plug
                componentList = self.outputList
                removeMethod = self.__remove_output

            if component.sourcePlug:
                component.sourcePlug.destinationPlugs.remove(component)
            for i in range(len(component.destinationPlugs)):
                plug = component.destinationPlugs[0]
                component.disconnect(plug)
                if Circuit.detailedRemoveVerbose:
                    log.debug(
                        "plug %s has been removed from %s sourcePlug"
                        % (component.name, self.name))

        elif isinstance(component, Circuit):    # it is a Circuit
            componentList = self.circuitList
            removeMethod = self.__remove_circuit
            for plug in component.inputList + component.outputList:
                component.remove(plug)          # remove all circuit's plugs
        else:                                   # it is an error
            log.error(
                "Cannot remove component because it is neither a Plug nor a "
                "Circuit.")
            return
        if component not in componentList:      # no need to remove the compon
            if Circuit.removePlugVerbose or Circuit.removeCircuitVerbose:
                log.info(
                    "Cannot remove component from list because "
                    "list have no such component")
            return
        removeMethod(component)                 # remove the compon from list

    # -+-----------------------    OTHER METHODS    -----------------------+- #
    def setName(self, name):
        if len(name):
            if name in [x.name for x in self.owner.circuitList]:
                log.error('name %s already in use' % (name,))
                return False
            else:
                log.info("%s.%s's name changed to %s" % (
                    self.owner.name, self.name, name,))
                self.name = name
                return True
        else:
            log.error('name must be at least one character long')
            return False

    def generate_name(self):
        """Generate a name for a Circuit (like 'NandGate4' or 'NotGate0')."""
        i = 0
        className = self.class_name().upper()  # get class name of the object
        names = [circuit.name for circuit in self.owner.circuitList]
        while True:
            name = str(className) + '_' + str(i)
            if name not in names:
                return name
            i += 1

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


#================================= FUNCTIONS =================================#
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
        c += eval('circuit.%s()' % (method,)) \
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
