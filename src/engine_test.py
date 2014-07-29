#!/usr/bin/env python3
# coding: utf-8

#############################################################
## quelques test de construction et simulation de circuits ##
##                sera remplacé par la GUI                 ##
#############################################################

from engine.simulator import log  # le log
from engine.gates import *        # portes logiques de base
from engine.circuits import *     # circuits logiques avancés
from engine.clock import *        # horloge


HEADER = '\033[95m'
BLUE = '\033[94m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
AUTO = '\033[0m'


def print_plug_info(plug):
    COLOR = GREEN if plug.value else RED
    print('%s: %s\n\tconnections: %s\n\tconnectedTo: %s'
            % (plug.name, COLOR + str(plug.value) + AUTO,
                str([conn.name for conn in plug.connections]),
                str([conn.name for conn in plug.connectedTo])))


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
def adder_2x4(a, b, TC):
    # composantes du circuit
    F0 = TC.add_circuit(FullAdder('F0'))
    F1 =TC. add_circuit(FullAdder('F1'))
    F2 =TC. add_circuit(FullAdder('F2'))
    F3 =TC. add_circuit(FullAdder('F3'))
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
    TC = Circuit("Main_Circuit", None)
    
    clk = TC.add_input('CLOCK')        # l'horloge est une simple sortie du TL
    bgClockThread = ClockThread(clk)   # mais elle est simulée dans un thread
    bgClockThread.start()              # on démarre l'horloge (1 tic par sec)

    AND = TC.add_circuit(AndGate)      # puis on créé une porte AND
    I0 = AND.inputList[0]
    I1 = AND.inputList[1]
    O0 = AND.outputList[0]

    I0.set(1)                          # on positionne son entrée I0 à 1
    clk.connect(I1)                    # on connecte l'horloge à son entrée I1
    
    sleep(bgClockThread.spd)           # on attends un tic d'horloge
    print(O0.value)                    # on imprime la sortie de la porte AND
    time.sleep(1)                      # on attends un second tic d'horloge
    print(O0.value)                    # le tic à modifié la sortie du AND
    time.sleep(1)                      # on attends encore un troisième tic
    print(O0.value)                    # la sortie vaut la valeur de l'horloge
                                       # logique car 1 ET 0 = 0 / 1 ET 1 = 1
    bgClockThread.stop()               # enfin on quite le thread de l'horloge

    #~ print('_____________________________________________________\n')
    #~ # on ajoute 2 entrées et 1 sortie au circuit du "top-level"
    #~ A = TC.add_input('A')
    #~ B = TC.add_input('B')
    #~ C = TC.add_output('C')
    #~ # on connecte les entrées et la sortie de TC à celles du circuit AndGate
    #~ TC.inputList[0].connect(TC.circuitList[0].inputList[0])
    #~ TC.inputList[1].connect(TC.circuitList[0].inputList[1])
    #~ TC.circuitList[0].outputList[0].connect(TC.outputList[0])
    #~ # on affiche les valeurs de la sortie de la porte AND et de celle de TC
    #~ print(TC.circuitList[0].outputList[0].value)    # => False
    #~ print(TC.outputList[0].value)                   # => False
    #~ # on positionne les entrées de TC à 1
    #~ TC.inputList[0].set(1)
    #~ TC.inputList[1].set(1)
    #~ # on réaffiche les valeurs de la sortie de TC et de celle du AndGate
    #~ print(TC.circuitList[0].outputList[0].value)   # => True
    #~ print(TC.outputList[0].value)                  # => True
    #~ # on a utilisé l'accès par index mais on aurait pu utiliser l'accès par nom
    #~ print(TC.inputList[0])                         # équivalent à...
    #~ print(TC.input('A'))
#~ 
    #~ print('_____________________________________________________\n')
    #~ adder_2x4('1011', '0010', TC)
#~ 
    #~ print('_____________________________________________________\n')
    #~ print('nb total de circuits: ' + str(total_nb_circuits(TC)))
    #~ print("nb total d'entrées:   " + str(total_nb_inputs(TC)))
    #~ print("nb total de sorties:  " + str(total_nb_outputs(TC)))
    #~ print("nb total d'E/S:       " + str(total_nb_plugs(TC)))

    #~ NOT = TC.add_circuit(NotGate)
    #~ GIN = TC.add_input()
    #~ GOUT = TC.add_output()
    #~ I = NOT.inputList[0]
    #~ O = NOT.outputList[0]
    #~ GIN.connect(I)
    #~ O.connect(GOUT)
    #~ GIN.set(False)
#~ 
    #~ print('________________________________________________________________\n')
    #~ for plug in [GIN, I, O, GOUT]:
        #~ print_plug_info(plug)
    #~ 
    #~ O.disconnect(GOUT)
    #~ print('\n___________________DISCONNECTED GOUT AND O____________________\n')
    #~ for plug in [GIN, I, O, GOUT]:
        #~ print_plug_info(plug)


