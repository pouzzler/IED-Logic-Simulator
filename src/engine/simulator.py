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

import logging


log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
fileHandler = logging.FileHandler('simulator.log')
stdoutHandler = logging.StreamHandler()
fileHandler.setLevel(logging.DEBUG)
stdoutHandler.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s %(levelname)s %(message)s',
    datefmt='%H:%M:%S')
fileHandler.setFormatter(formatter)
stdoutHandler.setFormatter(formatter)


class Plug:
    """Represents an input or output."""
    # Verbosity options :
    setInputVerbose = True      # log input.set()
    setOutputVerbose = True     # log output.set()
    connectVerbose = True       # log i/o.connect()

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
        # No change, nothing to do.
        if self.value == value and self.__nbEval != 0:
            return
        # else set the new value and update the circuit accordingly
        else:
            self.value = bool(value)
            self.__nbEval += 1
        if Plug.setInputVerbose and self.isInput:
            log.info(
                self.str_inputV
                % (self.owner.name, self.name, int(self.value),))
        if Plug.setOutputVerbose and not self.isInput:
            log.info(
                self.str_outputV
                % (self.owner.name, self.name, int(self.value),))
        # Gate input changed, set outputs values
        if self.isInput:
            self.owner.evalfun()
        # then, all plugs in the destination list are set to this value
        for dest in self.destinationPlugs:
            dest.set(value)

    def connect(self, other):
        """Connects two plugs, or logs the reason why not."""
        if self == other:   # invalid connections
            log.warning(self.str_connectOnItself)
            return False
        elif (
                self.owner.owner == other.owner.owner
                and self.isInput and other.isInput):
            log.warning(self.str_connectInOnIn)
            return False
        elif (
                self.owner.owner == other.owner.owner
                and not self.isInput and not other.isInput):
            log.warning(self.str_connectOutOnOut)
            return False
        elif (other == self.sourcePlug or self == other.sourcePlug):
            log.warning(self.str_connectAlreadyExists)
            return False
        elif (
                not self.isInput and other.isInput and
                self.owner.owner == other.owner):
            log.warning(self.str_connectGlobInLocOut)
            return False
        elif (
                self.isInput and not other.isInput and
                self.owner.owner == other.owner):
            log.warning(self.str_connectGlobOutLocIn)
            return False
        elif (
                not self.isInput and other.isInput and
                self.owner == other.owner.owner):
            log.warning(self.str_connectGlobInLocOut)
            return False
        elif (
                self.isInput and not other.isInput and
                self.owner == other.owner.owner):
            log.warning(self.str_connectGlobOutLocIn)
            return False
        else:
            if ((
                    self.owner.owner and not self.isInput) or
                    (not self.owner.owner and self.isInput)):
                if other.sourcePlug:
                    log.warning(
                        self.str_connectHasConnection
                        % (other.owner.name, other.name,))
                    return False
                else:
                    self.destinationPlugs.append(other)
                    other.sourcePlug = self
            else:
                if self.sourcePlug:
                    log.warning(
                        self.str_connectHasConnection
                        % (self.owner.name, self.name,))
                    return False
                else:
                    other.destinationPlugs.append(self)
                    self.sourcePlug = other
            if Plug.connectVerbose:
                log.info(
                    self.str_connect % (
                        other.owner.name, other.name, self.owner.name,
                        self.name,))
            return True

    def disconnect(self, plug):
        """Disconnect two plugs."""
        # INVALID disconnection
        if not(plug in self.destinationPlugs or self in plug.destinationPlugs):
            log.info(
                '%s.%s and %s.%s are not connected'
                % (self.owner.name, self.name, plug.owner.name, plug.name,))
            return
        # left => right disconnection
        elif plug in self.destinationPlugs:
            self.destinationPlugs.remove(plug)
            plug.sourcePlug = None
            plug.set(0)
        # right => left disconnection
        else:
            plug.destinationPlugs.remove(self)
            self.sourcePlug = None
            self.set(0)
        # disconnection successful: print a message
        log.info(
            self.str_disconnect
            % (self.owner.name, self.name, plug.owner.name, plug.name,))

    def setName(self, name):
        """Set the name of the plug."""
        if len(name):
            if (self.isInput and name in [
                    x.name for x in self.owner.inputList]) or \
                    (not self.isInput and name in [
                        x.name for x in self.owner.outputList]):
                log.error(self.str_unavailableName % (name,))
                return False
            else:
                log.info(self.str_changedName % (
                    self.owner.name, self.name, name,))
                self.name = name
                return True
        else:
            log.error(str_nameLen)
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


class Circuit:
    """Represents a logic circuit."""
    # Verbosity options :
    addPlugVerbose = True         # log self.add_plug()
    addCircuitVerbose = True      # log self.add_circuit()
    removePlugVerbose = True      # log self.remove_plug()
    removeCircuitVerbose = True   # log self.remove_circuit()
    detailedRemoveVerbose = True  # Detailed remove

    def __init__(self, name, owner, category=None):
        self.owner = owner      # parent circuit
        self.name = self.generate_name() if name is None else name
        self.category = category    # used to identify user circuits
        self.inputList = []
        self.outputList = []
        self.circuitList = []
        log.info(
            self.str_circuitCreated
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

    def remove_circuit(self, circuit):
        """Remove a circuit from the circuitList of the circuit."""
        self.circuitList.remove(circuit)
        Circuit.removePlugVerbose
        if Circuit.removeCircuitVerbose:
            log.info(
                "circuit %s '%s' removed from %s"
                % (circuit.class_name(), circuit.name, self.name,))

    def remove(self, component):
        """Remove a component (Plug or Circuit) from the circuit."""
        # if the object is a Plug...
        if isinstance(component, Plug):
            if component.isInput:
                componentList = self.inputList
                removeMethod = self.remove_input
            else:
                componentList = self.outputList
                removeMethod = self.remove_output
            # disconnect the plug and its source
            if component.sourcePlug:
                component.sourcePlug.disconnect(component)
            # disconnect all Plugs connected to this plug
            for i in range(len(component.destinationPlugs)):
                component.disconnect(component.destinationPlugs[0])
        # if the object is a Circuit...
        elif isinstance(component, Circuit):
            componentList = self.circuitList
            removeMethod = self.remove_circuit
            # remove all circuit's plugs
            for plug in component.inputList + component.outputList:
                component.remove(plug)
        # if it is not a Plug nor a Circuit...
        else:
            log.error(
                "cannot remove component because it is neither a Plug nor a "
                "Circuit")
            return False
        # the object is not in the list
        if component not in componentList:
            if Circuit.removePlugVerbose or Circuit.removeCircuitVerbose:
                log.info(
                    "Cannot remove component from list because "
                    "list have no such component")
            return False
        # remove tthe object from the correct list
        removeMethod(component)
        return True

    # -+-----------------------    OTHER METHODS    -----------------------+- #
    def setName(self, name):
        """Set the name of the circuit."""
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
