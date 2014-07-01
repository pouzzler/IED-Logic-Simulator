#!/usr/bin/env python3
# coding: utf-8

#############################################################
## quelques test de construction et simulation de circuits ##
##                sera remplacé par la GUI                 ##
#############################################################

from simulator import _TC  # le circuit du "top-level"
from gates import *        # portes logiques de base
from circuits import *     # circuits logiques avancés
from clock import *        # horloge


# un simple nand
def nand(a, b):
    # composantes du circuit
    NA0 = NandGate('NA1')
    # positionnement des valeurs d'entrée
    NA0.A.set(a)    # bitA
    NA0.B.set(b)    # bitB
    # affichage des valeurs de sortie
    print('%i' % (int(NA0.C.value)))


# retourne la valeur du bit 'bit' dans x
def bit(x, bit):
    return x[bit] == '1'


# additionneur de 2 mots de 4 bits
def adder_2x4(a, b):
    # composantes du circuit
    F0 = add_circuit(FullAdder('F0'))
    F1 = add_circuit(FullAdder('F1'))
    F2 = add_circuit(FullAdder('F2'))
    F3 = add_circuit(FullAdder('F3'))
    # connexions des composantes du circuit
    F0.output('Cout').connect(F1.input('Cin'))
    F1.output('Cout').connect(F2.input('Cin'))
    F2.output('Cout').connect(F3.input('Cin'))
    # positionnement des valeurs d'entrée
    F0.input('A').set(bit(a, 3))    # bit0 wordA
    F0.input('B').set(bit(b, 3))    # bit0 wordB
    F0.input('Cin').set(0)          # retenue_entrante
    F1.input('A').set(bit(a, 2))    # bit1 wordA
    F1.input('B').set(bit(b, 2))    # bit1 wordB
    F2.input('A').set(bit(a, 1))    # bit2 wordA
    F2.input('B').set(bit(b, 1))    # bit2 wordB
    F3.input('A').set(bit(a, 0))    # bit3 wordA
    F3.input('B').set(bit(b, 0))    # bit3 wordB
    # affichage des valeurs de sortie
    print('%i%i%i%i%i' % (int(F3.Cout.value), int(F3.S.value), int(F2.S.value),
                          int(F1.S.value), int(F0.S.value)))


#================================= PROGRAMME =================================#
from time import sleep


if __name__ == '__main__':
    clk = add_output('CLOCK')          # l'horloge est une simple sortie du TL
    bgClockThread = ClockThread(clk)   # mais elle est simulée dans un thread
    bgClockThread.start()              # on démarre l'horloge (1 tic par sec)
    AND = add_circuit(AndGate('AND'))  # puis on créé une porte AND
    AND.input('I0').set(1)             # on positionne son entrée I0 à 1
    clk.connect(AND.input('I1'))       # on connecte l'horloge à son entrée I1
    sleep(bgClockThread.spd)           # on attends un tic d'horloge
    print(AND.output('O').value)       # on imprime la sortie de la porte AND
    time.sleep(1)                      # on attends un second tic d'horloge
    print(AND.output('O').value)       # le tic à modifié la sortie du AND
    time.sleep(1)                      # on attends encore un troisième tic
    print(AND.output('O').value)       # la sortie vaut la valeur de l'horloge
                                       # logique car 1 ET 0 = 0 / 1 ET 1 = 1
    bgClockThread.stop()               # enfin on quite le thread de l'horloge

    print('_____________________________________________________\n')
    # on ajoute 2 entrées et 1 sortie au circuit du "top-level"
    add_input('A')
    add_input('B')
    add_output('C')
    # on connecte les entrées et la sortie de _TC à celles du circuit AndGate
    _TC.inputList[0].connect(_TC.circuitList[0].inputList[0])
    _TC.inputList[1].connect(_TC.circuitList[0].inputList[1])
    _TC.circuitList[0].outputList[0].connect(_TC.outputList[0])
    # on affiche les valeurs de la sortie de la porte AND et de celle de _TC
    print(_TC.circuitList[0].outputList[0].value)    # => False
    print(_TC.outputList[0].value)                   # => False
    # on positionne les entrées de _TC à 1
    _TC.inputList[0].set(1)
    _TC.inputList[1].set(1)
    # on réaffiche les valeurs de la sortie de _TC et de celle du AndGate
    print(_TC.circuitList[0].outputList[0].value)   # => True
    print(_TC.outputList[0].value)                  # => True
    # on a utilisé l'accès par index mais on aurait pu utiliser l'accès par nom
    print(_TC.inputList[0])                         # équivalent à...
    print(_TC.input('A'))

    print('_____________________________________________________\n')
    adder_2x4('1011', '0010')

    print('_____________________________________________________\n')
    print('nb total de circuits: ' + str(total_nb_circuits()))
    print("nb total d'entrées:   " + str(total_nb_inputs()))
    print("nb total de sorties:  " + str(total_nb_outputs()))
    print("nb total d'E/S:       " + str(total_nb_plugs()))
    
    toto = AndGate()
    print(toto.nb_inputs())
    print(toto.class_name())
