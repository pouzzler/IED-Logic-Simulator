#!/usr/bin/env python3
# coding: utf-8

##########################################################################
## tente de simuler les portes et circuits logiques en python, sans GUI ##
##########################################################################

from comod import _INPUT
from comod import _OUTPUT
from comod import _CIRCUIT


#============================ MOTEUR DU SIMULATEUR ===========================#
#        -+------------------------ CLASSES ------------------------+-        #
# classe des connecteurs, un connecteurs est une entrée ou une sortie
class Plug:
    # initialise le plug
    def __init__(self, ptype, name, owner, printval):
        self.owner = owner        # circuit ou porte disposant de cette E/S
        self.name = name          # son nom
        self.ptype = ptype        # indique s'il faut réévaluer les valeurs
        self.printval = printval  # indique s'il faut afficher sa valeur
        self.value = False        # au départ pas de courant
        self.nbEval = 0           # nombre de fois évalué
        self.connections = []     # listes des plugs connectés

    # usage plug.set([0/1])
    def set(self, value):
        if self.value == value and self.nbEval != 0:  # valeur inchangée, sors!
            return
        else:                           # sinon positionne la nouvelle valeur
            self.value = bool(value)
            self.nbEval += 1
        if self.ptype is _INPUT:        # entrée? il faut réévaluer le circuit
            self.owner.evalfun()
        if self.printval:               # afficher la valeur du plug ?
            print('%s.%s: %i' % (self.owner.name, self.name, int(self.value)))
        for connection in self.connections:
            connection.set(value)       # change la valeur des pkugs connectés

    # usage: plugE.connect([plugA, plugB, ..., plugN]) / plugE.connect(plugA)
    def connect(self, inputs):
        if not isinstance(inputs, list):
            inputs = [inputs]               # transforme en liste
        for input in inputs:
            self.connections.append(input)  # ajoute les connexion


# pour les circuits logiques
class Circuit:
    # initialise le circuit
    def __init__(self, name):
        self.name = name        # nom (facultatif)
        self.inputList = []     # liste des entrées du circuit
        self.outputList = []    # liste des sorties du circuit
        self.circuitList = []   # liste des circuits du circuit
        print('> %s has been created' % (self.name))

    # ajoute un plug (entrée ou sortie) dans la liste approprié du circuit
    def add_plug(self, plug):
        if plug.ptype is _INPUT:
            self.inputList.append(plug)
        elif plug.ptype is _OUTPUT:
            self.outputList.append(plug)
        else:
            exit('add_plug: wrong plug type')
        print('    + plug %s add to %s.xxxputList' % (plug.name, self.name,))

    # ajoute une entrée à la liste inputList du circuit
    def add_input(self, name=None, printval=False):
        self.inputList.append(Plug(_INPUT, name, self, printval))
        print("    + plug '%s' add to %s.inputList" % (name, self.name,))
        return self.inputList[-1]

    # ajoute une sortie à la liste outputList du circuit
    def add_output(self, name=None, printval=False):
        self.outputList.append(Plug(_OUTPUT, name, self, printval))
        print("    + plug '%s' add to %s.outputList" % (name, self.name,))
        return self.outputList[-1]

    # ajoute un circuit à la liste circuitList du circuit
    def add_circuit(self, circuit):
        self.circuitList.append(circuit)
        print("  + circuit %s '%s' add to %s.circuitsList" %
              (circuit.class_name(), circuit.name, self.name,))
        return self.circuitList[-1]

    # retourne le nom de la classe d'origine du circuit
    def class_name(self):
        return self.__class__.__name__

    # retourne l'entrée du circuit de nom inputName
    def input(self, inputName):
        for input in self.inputList:
            if input.name == inputName:
                return input

    # retourne la sortie du circuit de nom outputName
    def output(self, outputName):
        for output in self.outputList:
            if output.name == outputName:
                return output

    # retourne le circuit du circuit de nom circuitName
    def circuit(self, circuitName):
        for cicuit in self.circuitList:
            if cicuit.name == circuitName:
                return cicuit

    # retourne le nombre d'entrées du circuit
    def nb_inputs(self):
        return len(self.inputList)

    # retourne le nombre de sortie du circuit
    def nb_outputs(self):
        return len(self.outputList)

    # retourne le nombre d'entrées/sorties du circuit
    def nb_plugs(self):
        return self.nb_inputs() + self.nb_outputs()

    # retourne le nombre de circuits du circuit
    def nb_circuits(self):
        return len(self.circuitList)

    # seule les classe enfant peuvent avoir une fonction logique
    def evalfun(self):
        return


#        -+---------------------- UTILITAIRES ----------------------+-        #
# affiche les connecteurs d'un circuit et des circuits qui le constitue
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
#        -+------------ AJOUTER DES OBJETS AU TOP-LEVEL ------------+-        #
# ajoute un entrée/sortie à la liste des entrées/sorties du circuit "top-level"
def add_plug(plug):
    return _TC.add_plug(plug)


# ajoute une entré à la liste des entrées du circuit "top-level"
def add_input(name=None, printval=False):
    return _TC.add_input(name, printval)


# ajoute une sortie à la liste des sorties du circuit "top-level"
def add_output(name=None, printval=False):
    return _TC.add_output(name, printval)


# ajoute un circuit à la liste des circuit du circuit "top-level"
def add_circuit(name=None):
    return _TC.add_circuit(name)


#        -+-------- ACCÉDER AUX OBJETS DU TOP-LEVEL PAR NOM --------+-        #
# retourne l'entrée du circuit "top-level" de nom inputName
# /!\ override la fonction input de python 3
def input(inputName):
    return _TC.input(inputName)


# retourne l'entrée du circuit "top-level" de nom inputName
def output(outputName):
    return _TC.input(outputName)


# retourne l'entrée du circuit "top-level" de nom inputName
def circuit(circuitName):
    return _TC.input(circuitName)


#        -+-------------- NOMBRE D'OBJETS DU TOP-LEVEL -------------+-        #
# calcule le nombre d'entrées et/ou de sorties dans une liste de circuits
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


# calcule le nombre total d'entrées utilisés
def total_nb_inputs():
    return count_items([_TC], _INPUT)


# calcule le nombre total de sorties utilisés
def total_nb_outputs():
    return count_items([_TC], _OUTPUT)


# calcule le nombre total d'E/S utilisés
def total_nb_plugs():
    return count_items([_TC], _INPUT + _OUTPUT)


# calcule le nombre total de circuits utilisés (incluant les sous-circuits)
def total_nb_circuits():
    return count_items([_TC], _CIRCUIT)


#============================= VARIABLES GLOBALES ============================#
# on créé un circuit TC qui contiendra des E/S ainsi que d'autres circuits
# c'est le circuit du top-level qui correspond à la zone de dessin de la gui
# en effet, la zone de dessin contient des E/S et des circuits (notemment des
# portes logiques) on peut donc la considérer elle-même comme un circuit
_TC = Circuit('TOP_CIRCUIT_0')
