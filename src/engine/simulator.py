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
# Contain the engine. It's an event-driven, multi-delayed and three-valued    #
# engine. It implement the Circuit class for the logic gates (gates.py) and   #
# the Plug classe for Circuits I/O.                                           #
# --------------------------------------------------------------------------- #
# TODO: in set(), clock the unstable connection so that its value change from #
#       True to False at regular time interval (use a global clock).          #
###############################################################################


import sys
import time
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


recursionNb_ = 0
gateList_ = []
exceed_ = False


class Agenda:
    """This class handle the propagation of the events. It contain a priority
    queue of segments wich describe events (delay + operation). Th events
    are added on the queue so that they're sort from the nearest to the
    farthest. The agenda can then execute the scheduled events (outputs
    changes) by propagating them.
    """
    def __init__(self):
        self.currentTime = 0
        self.timeSegments = []

    def is_empty(self):
        """Return True if there is no scheduled action."""
        return False if self.timeSegments else True

    def get_current_time(self):
        """Return the current time of the agenda."""
        return self.currentTime

    def add_segment(self, time, action, name):
        """Add a segment and sort the queue from nearest to farthest event."""
        self.timeSegments.append((time, action, name))
        self.timeSegments.sort(key=lambda item: item[0])

    def propagate(self):
        """Propagate the events of tge queue: pop closest event and execute it
        then continue until no event remains on the queue.
        """
        if self.is_empty():
            return 1
        proc = self.pop_first_item()
        try:
            proc()
        except RuntimeError:
            return 0
        return self.propagate()

    def pop_first_item(self):
        """Return the nearest event of the queue."""
        segment = self.timeSegments[0]
        self.currentTime = segment[0]
        self.timeSegments = self.timeSegments[1:]
        # here we can implement simu speed with segment[0] - self.currentTime
        return segment[1]

    def schedule(self, gate, proc):
        """Add an event segment (execution time, function, function name) to
        the events queue.
        """
        self.add_segment(
            self.get_current_time() + gate.delay,
            proc,
            gate.__class__.__name__ + ' evalfun')


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
        self.generate_name(name)
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

    def generate_name(self, name, prefix=None):
        """Generate a name for a plug."""
        i = 0
        names = [io.name for io in (
            self.owner.inputList if self.isInput else self.owner.outputList)]
        if name and prefix:
            name = None
        if name and name not in names:
            self.name = name
            return
        prefix = prefix if prefix else ('in' if self.isInput else 'out')
        while True:
            name = prefix + str(i)
            if name not in names:
                self.name = name
                return
            i += 1

    def set(self, value, forced=False):
        """Try to set the value of a Plug. If the connection don't became
        stable set the value to None.
        """
        global exceed_
        exceed_ = False
        self.do_set(value, forced)
        if exceed_:
            self.do_set(None)

    def do_set(self, value, forced=False):
        """Sets the boolean value of a Plug."""
        global recursionNb_
        global gateList_
        global exceed_
        # no change, nothing to do.
        if self.value == value and self.__nbEval != 0 and not forced:
            return
        # If you reach the recursion limit: stop, let set() set it to unstable
        recursionNb_ += 1
        if self.owner not in gateList_:
            gateList_.append(self.owner)
        if recursionNb_ > len(gateList_) * 10:
            recursionNb_ = 0
            gateList_ = []
            exceed_ = True
            return
        # else set the new value and update the circuit accordingly
        self.value = value
        if not forced:
            self.__nbEval += 1
        if Plug.setInputVerbose and self.isInput:
            log.info(
                self.str_inputV % (self.owner.name, self.name,
                str(self.value),))
        if Plug.setOutputVerbose and not self.isInput:
            log.info(
                self.str_outputV % (self.owner.name, self.name,
                str(self.value),))
        # gate input changed: set outputs values
        if self.isInput:
            self.owner.evalfun()
        agenda_.propagate()
        # then, all plugs in the destination list are set to the same value
        for dest in self.destinationPlugs:
            dest.do_set(value)
        recursionNb_ -= 1
        gateList_ = []

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

    def init_inputs(self):
        for inp in self.inputList:
            inp.set(False, True)

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
            log.info(self.str_newName % (self.owner.name, self.name, name,))
            self.name = name
            return True

###############################################################################
###############################################################################
# the main agenda use for the simulation, there should be only one agenda
agenda_ = Agenda()
