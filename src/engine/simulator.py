#!/usr/bin/env python3
# coding: utf-8

from copy import deepcopy
import logging


log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
fileHandler = logging.FileHandler('simulator.log')
stdoutHandler = logging.StreamHandler()
fileHandler.setLevel(logging.DEBUG)
stdoutHandler.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s %(levelname)s %(message)s', datefmt='%H:%M:%S')
fileHandler.setFormatter(formatter)
stdoutHandler.setFormatter(formatter)


class Plug:
    """Represents an input or output."""
    # Verbosity options :
    addPlugVerbose = True       # Log self.__init__()?
    setInputVerbose = True      # Log input.set()?
    setOutputVerbose = True     # Log output.set()?
    connectVerbose = True       # Log i/o.connect()?

    def __init__(self, isInput, name, owner):
        self.isInput = isInput
        self.owner = owner
        self.name = self.generate_name() if name is None else name
        self.value = False
        self.__nbEval = 0
        self.sourcePlug = None
        self.destinationPlugs = []
        if self.isInput:            # Add plug to owner.
            owner.inputList.append(self)
            if Plug.addPlugVerbose:
                log.info(self.str_inputAdded % (self.name, owner.name,))
        else:
            owner.outputList.append(self)
            if Plug.addPlugVerbose:
                log.info(self.str_outputAdded % (self.name, owner.name,))

    def connect(self, other):
        """Connects two plugs, or logs the reason why not."""
        if self == other:
            log.warning(self.str_connectOnItself)
            return False
        elif (  # same scope input and input
                self.isInput and other.isInput
                and self.owner.owner == other.owner.owner):
            log.warning(self.str_connectInOnIn)
            return False
        elif (  # same scope output and output
                not self.isInput and not other.isInput
                and self.owner.owner == other.owner.owner):
            log.warning(self.str_connectOutOnOut)
            return False
        elif (  # these two plus are already connected
                other == self.sourcePlug or self == other.sourcePlug):
            log.warning(self.str_connectAlreadyExists)
            return False
        elif (  # global input and local output
                not self.isInput and other.isInput and
                self.owner.owner == other.owner):
            log.warning(self.str_connectGlobInLocOut)
            return False
        elif (  # global output and local input
                self.isInput and not other.isInput and
                self.owner.owner == other.owner):
            log.warning(self.str_connectGlobOutLocIn)
            return False
        elif (  # global input and local output
                not self.isInput and other.isInput and
                self.owner == other.owner.owner):
            log.warning(self.str_connectGlobInLocOut)
            return False
        elif (  # global output and local input
                not self.isInput and other.isInput and
                self.owner == other.owner.owner):
            log.warning(self.str_connectGlobOutLocIn)
            return False
        else:
            if ((   # origin is self
                    self.owner.owner and not self.isInput) or
                    (not self.owner.owner and self.isInput)):
                if other.sourcePlug:    # but other is already connected
                    log.warning(
                        self.str_connectHasConnection
                        % (other.owner.name, other.name,))
                    return False
                else:
                    self.destinationPlugs.append(other)
                    other.sourcePlug = self
                    other.set(self.value)
            else:   # origin is other
                if self.sourcePlug:    # but self is already connected
                    log.warning(
                        self.str_connectHasConnection
                        % (self.owner.name, self.name,))
                    return False
                else:
                    other.destinationPlugs.append(self)
                    self.sourcePlug = other
                    self.set(other.value)
            if Plug.connectVerbose:
                log.warning(    # We want it to appear in MainView
                    self.str_connect % (
                        other.owner.name, other.name, self.owner.name,
                        self.name,))
            return True

    def disconnect(self, other):
        """Disconnect two plugs."""
        # Invalid disconnection.
        if not (
                other in self.destinationPlugs
                or self in other.destinationPlugs):
            log.info(
                self.str_invalidDisconnect
                % (self.owner.name, self.name, other.owner.name, other.name,))
            return
        elif other in self.destinationPlugs:     # source = self
            self.destinationPlugs.remove(other)
            other.sourcePlug = None
            other.set(0)
        else:                                   # source = other
            other.destinationPlugs.remove(self)
            self.sourcePlug = None
            self.set(0)
        log.info(
            self.str_disconnect
            % (self.owner.name, self.name, other.owner.name, other.name,))

    def generate_name(self):
        """Generate a name for a plug."""
        i = 0
        names = [io.name for io in (
            self.owner.inputList if self.isInput else self.owner.outputList)]
        while True:
            name = ('in' if self.isInput else 'out') + str(i)
            if name not in names:
                return name
            i += 1

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

    def setName(self, name):
        """Set the name of the plug."""
        if not len(name):
            log.error(self.str_nameLen)
            return False
        names = (
            [x.name for x in self.owner.inputList] if self.isInput
            else [x.name for x in self.owner.outputList])
        if name in names:
            log.error(self.str_unavailableName % (name,))
            return False
        else:
            log.info(self.str_newName % (self.owner.name, self.name, name,))
            self.name = name
            return True


class Circuit:
    """Represents a logic circuit."""
    # Verbosity options :
    addCircuitVerbose = True      # Log self.add_circuit()?
    removePlugVerbose = True      # Log self.remove_plug()?
    removeCircuitVerbose = True   # Log self.remove_circuit()?
    detailedRemoveVerbose = True  # ?

    def __init__(self, name, owner, category=None):
        self.owner = owner
        self.name = self.generate_name() if name is None else name
        self.category = category   # Used to identify user circuits.
        self.inputList = []
        self.outputList = []
        self.circuitList = []
        log.info(self.str_circuitCreated % (self.class_name(), self.name,))
        if owner:
            owner.circuitList.append(self)
            if Circuit.addCircuitVerbose:
                log.info(
                    self.str_circuitAdded
                    % (self.class_name(), self.name, self.owner.name,))        

    def add(self, component):
        """Used when loading circuits, to add pre-existing components."""
        component.owner = self
        if isinstance(component, Circuit):
            self.circuitList.append(component)
        elif component.isInput:
            self.inputList.append(component)
        else:
            self.outputList.append(component)

    def class_name(self):
        """Return the class name of this circuit."""
        return self.__class__.__name__

    def clear(self):
        """Empties the circuit of all components."""
        self.inputList = []
        self.outputList = []
        self.circuitList = []

    def evalfun(self):
        """Only builtin gates have an evalfun."""
        pass

    def generate_name(self):
        """Generate a name for this circuit."""
        i = 0
        className = self.class_name()
        names = [circuit.name for circuit in self.owner.circuitList]
        while True:
            name = className + str(i)
            if name not in names:
                return name
            i += 1

    def nb_inputs(self):
        """Returns the number of inputs in the circuit."""
        return len(self.inputList)

    def nb_outputs(self):
        """Returns the number of outputs in the circuit."""
        return len(self.outputList)

    def remove(self, component):
        """Remove a component (Plug or Circuit) from the circuit."""
        if isinstance(component, Plug):
            if component.isInput:
                componentList = self.inputList
                removeMethod = self.remove_input
            else:
                componentList = self.outputList
                removeMethod = self.remove_output
        elif isinstance(component, Circuit):
            componentList = self.circuitList
            removeMethod = self.remove_circuit
        else:   # Not a valid circuit component.
            log.warning(self.str_invalidComponent)
            return False
        if component not in componentList:
            log.warning(self.str_invalidRem)
            return False
        if isinstance(component, Plug):     # Remove the item.
            if component.sourcePlug:
                component.sourcePlug.disconnect(component)
            for i in range(len(component.destinationPlugs)):
                component.disconnect(component.destinationPlugs[0])
        else:
            for plug in component.inputList + component.outputList:
                component.remove(plug)
        removeMethod(component)
        return True

    def remove_circuit(self, circuit):
        """Remove a circuit from the circuitList of the circuit."""
        self.circuitList.remove(circuit)
        Circuit.removePlugVerbose
        if Circuit.removeCircuitVerbose:
            log.info(
                self.str_circuitRem
                % (circuit.class_name(), circuit.name, self.name,))

    def remove_input(self, input):
        """Remove an input from the inputList of the circuit."""
        self.inputList.remove(input)
        if Circuit.removePlugVerbose:
            log.info(self.str_inputRem % (input.name, self.name,))

    def remove_output(self, output):
        """Remove an output from the outputList of the circuit."""
        self.outputList.remove(output)
        if Circuit.removePlugVerbose:
            log.info(self.str_outputRem % (output.name, self.name,))

    def setName(self, name):
        """Set the name of this circuit."""
        if not len(name):
            log.error(self.str_nameLen)
            return False
        elif name in [x.name for x in self.owner.circuitList]:
            log.error(self.str_unavailableName % (name,))
            return False
        else:
            log.info(
                self.str_newName % (self.owner.name, self.name, name,))
            self.name = name
            return True
