#!/usr/bin/env python3
# coding: utf-8


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


MAGENTA = '\033[95m'
BLUE = '\033[94m'
GREEN = '\033[92m'
ORANGE = '\033[93m'
RED = '\033[91m'
AUTO = '\033[0m'
_INDENT_ = ''
gateList=[]
exceed_ = False


class Agenda:
    def __init__(self):
        self.currentTime = 0
        self.timeSegments = []

    def is_empty(self):
        return False if self.timeSegments else True

    def get_current_time(self):
        return self.currentTime

    def add_segment(self, time, action, name):
        self.timeSegments.append((time, action, name))
        self.timeSegments.sort(key=lambda item: item[0])
        #~ print(_INDENT_ + BLUE + "+ scheduling '%s' at %i" % (name, time) + AUTO)

    def propagate(self):
        # the queue is empty: stop!
        if self.is_empty():
            #~ print(_INDENT_ + GREEN + 'Agenda Propagation Done.' + AUTO)
            return 1
        #~ else:
            #~ print(_INDENT_ + ORANGE + 'Number of segments: ' +  str(len(self.timeSegments)) + AUTO)
        # pop first item of the queue and execute its procedure
        proc = self.pop_first_item()
        try:
            proc()
        except RuntimeError:
            print('/!\ ===== MAXIMUM RECURSION DEPTH ===== /!\\')
            return 0
        # recursion
        return self.propagate()

    def pop_first_item(self):
        segment = self.timeSegments[0]
        wait = segment[0] - self.currentTime
        self.currentTime = segment[0]
        self.timeSegments = self.timeSegments[1:]
        #~ for s in range(wait - 1, -1, -1):
            #~ print('.' * (len(_INDENT_) - 1) + " %d" % (self.currentTime - s))
            #~ time.sleep(0.2)
        #~ print(_INDENT_ + RED + "- executing '%s' at %d" % (segment[2], self.currentTime) + AUTO)
        return segment[1]

    def schedule(self, gate, proc):
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

    def isValidConnection(self, plug):
        """Check whether the connection left => right is valid or not"""
        if (
            # a connection is valid if it is from left to right:
            (   # parent Input => child Input
                self.isInput and
                plug.isInput and
                self.parent() is plug.grandparent()) or
            (   # parent Input => parent Output
                self.isInput and
                not plug.isInput and
                self.parent() is plug.parent()) or
            (   # child Output => parent Output
                not self.isInput and
                not plug.isInput and
                self.grandparent() is plug.parent()) or
            (   # child Output => child Input
                not self.isInput and
                plug.isInput and
                self.grandparent() is plug.grandparent())):
                # connection has been successfuly established
                if Plug.connectVerbose:
                    log.info(
                        '%s.%s connected to %s.%s'
                        % (self.owner.name, self.name, plug.owner.name,
                            plug.name))
                return True

    def isValidReversedConnection(self, plug):
        """Check whether the connection right => left is valid or not"""
        # reversed VALID connections
        if (
            # if the user connect from right to left we just have to invert
            # the conenction direction so these connections are also valid:
            (   # child Input => parent Input
                self.isInput and
                plug.isInput and
                self.grandparent() is plug.parent()) or
            (   # parent Output => parent Input
                not self.isInput and
                plug.isInput and
                self.parent() is plug.parent()) or
            (   # parent Output => child Output
                not self.isInput and
                not plug.isInput and
                self.parent() is plug.grandparent()) or
            (   # child Input => child Output
                self.isInput and
                not plug.isInput and
                self.grandparent() is plug.grandparent())):
                # connection has been successfuly established
                if Plug.connectVerbose:
                    log.info(
                        '%s.%s connected to %s.%s'
                        % (plug.owner.name, plug.name, self.owner.name,
                            self.name))
                return True

    def isInvalidConnection(self, plug):
        """Look for invalid connections and print a message accordingly."""
        # INVALID connection:
        #   * I/O => same I/O
        if plug is self:
            log.warning('cannot connect I/O on itself')
        #   * destination plug already have a source
        elif plug.sourcePlug:
            log.warning(
                '%s.%s already have an incoming connection'
                % (plug.owner.name, plug.name))
        elif (    #   * child Input => child Input
                self.isInput and
                plug.isInput and
                self.grandparent() is plug.grandparent()):
                    log.warning(
                        'cannot connect two Inputs from the same scope')
        elif (    #   * child Input => parent Output
                self.isInput and
                not plug.isInput and
                self.grandparent() is plug.parent()):
                    log.warning(
                        'cannot connect an Input on its parent Output')
        elif (    #   * child Output => child Output
                not self.isInput and
                not plug.isInput and
                self.grandparent() is plug.grandparent()):
                    log.warning(
                        'cannot connect two outputs from the same scope')
        elif (    #   * child Output => parent Input
                not self.isInput and
                plug.isInput and
                self.grandparent() is plug.parent()):
                    log.warning(
                        'cannot connect an Output on its parent Input')
        elif (    #   * parent Input => child Output
                self.isInput and
                not plug.isInput and
                self.parent() is plug.grandparent()):
                    log.warning(
                        'cannot connect an Input on its child Output')
        elif (    #   * parent Input => parent Input
                self.isInput and
                not plug.isInput and
                self.parent() is plug.parent()):
                    log.warning(
                        'cannot connect two Inputs from the same scope')
        elif (    #   * parent Output => child Input
                not self.isInput and
                not plug.isInput and
                self.parent() is plug.grandparent()):
                    log.warning(
                        'cannot connect an Output on its child Input')
        elif (    #   * parent Output => parent Output
                not self.isInput and
                not plug.isInput and
                self.parent() is plug.parent()):
                    log.warning(
                        'cannot connect two Outputs from the same scope')
        else:
            return False
        return True

    def parent(self):
        """Return the parent of the plug."""
        return self.owner

    def grandparent(self):
        """Return the grandparent of the plug."""
        return self.parent().owner

    def connect(self, plugList):
        """Connects a Plug to a list of Plugs."""
        if not isinstance(plugList, list):
            plugList = [plugList]
        for plug in plugList:
            # connection already exists
            if plug in self.destinationPlugs:
                log.info(
                    'connection between %s and %s already exists'
                    % (self.name, plug.name))
                continue
            
            # INVALID connections:
            if self.isInvalidConnection(plug):
                return False
            # VALID connections:
            # right => left connection
            if self.isValidReversedConnection(plug):
                plug.destinationPlugs.append(self)
                self.sourcePlug = plug
                self.set(plug.value)
            # left => right connection
            elif self.isValidConnection(plug):
                self.destinationPlugs.append(plug)
                plug.sourcePlug = self
                plug.set(self.value)
            # should not happens
            else:
                log.warning('engine cannot handle this connection')
                return False
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
            # problèmes de doublons si une des plugs s'appele déjà comme ça, je pense
        if name and name not in names:
            self.name = name
            return
        prefix = prefix if prefix else ('in' if self.isInput else 'out')
        while True:
            name =  prefix + str(i)
            if name not in names:
                self.name = name
                return
            i += 1

    def set(self, value, forced=False):
        global exceed_
        exceed_ = False
        res = self.do_set(value, forced)
        if res == 0 or exceed_:
            print('/!\ ===== RECURSION LIMIT EXCEEDED ===== /!\\')
            self.do_set(None, False)

    def do_set(self, value, forced=False):
        global _INDENT_
        global gateList
        global exceed_

        """Sets the boolean value of a Plug."""
        # no change, nothing to do.
        if self.value == value and self.__nbEval != 0 and not forced:
            return 2
        # If you reach the recursion limit: return 0
        _INDENT_ += '    '
        if self.owner not in gateList:
            gateList.append(self.owner)
        if (len(_INDENT_) / 4) > (len(gateList) * 10):
            _INDENT_ = ''
            gateList = []
            exceed_ = True
            return 0
        # else set the new value and update the circuit accordingly
        self.value = value

        if value == False:
            val = RED + 'False' + AUTO
        elif value == True:
            val = GREEN + 'True' + AUTO
        else:
            val = ORANGE + 'Unknown' + AUTO
        print(MAGENTA + "'%s.%s' set to " % (self.owner.name, self.name) + val)
        
        if not forced:
            self.__nbEval += 1
        if Plug.setInputVerbose and self.isInput:
            log.info(
                self.str_inputV
                % (self.owner.name, self.name, self.value,))
        if Plug.setOutputVerbose and not self.isInput:
            log.info(
                self.str_outputV
                % (self.owner.name, self.name, self.value,))

        # Gate input changed, set outputs values
        if self.isInput:
            self.owner.evalfun()
        agenda_.propagate()
        # then, all plugs in the destination list are set to this value
        for dest in self.destinationPlugs:
            dest.do_set(value, False)

        _INDENT_ = _INDENT_[4:]
        gateList = []
        return 1

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
            log.info(
                self.str_newName % (self.owner.name, self.name, name,))
            self.name = name
            return True

###############################################################################
###############################################################################
agenda_ = Agenda()
