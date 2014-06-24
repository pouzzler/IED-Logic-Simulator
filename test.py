#!/usr/bin/env python3
# coding: utf-8

#############################################################
## quelques test de construction et simulation de circuits ##
##                sera remplacé par la GUI                 ##
#############################################################

from gates import *		# portes logiques de base
from circuits import *	# circuits logiques avancés
from clock import *		# horloge

# un simple nand
def nand(a, b):
	# composantes du circuit
	NA0 = NandGate('NA1')
	# positionnement des valeurs d'entrée
	NA0.A.set(a)	# bitA
	NA0.B.set(b)	# bitB
	# affichage des valeurs de sortie
	print('%i' %(int(NA0.C.value)))

# retourne la valeur du bit 'bit' dans x
def bit(x, bit): return x[bit] == '1'

# additionneur de 2 mots de 4 bits
def adder_2x4(a, b):
	# composantes du circuit
	F0 = FullAdder('F0')
	F1 = FullAdder('F1')	# il nous faut 4 additionneurs complets
	F2 = FullAdder('F2')
	F3 = FullAdder('F3')
	# connexions des composantes du circuit
	F0.Cout.connect(F1.Cin)
	F1.Cout.connect(F2.Cin)	# il faut aussi propager la retenue
	F2.Cout.connect(F3.Cin)
	# positionnement des valeurs d'entrée
	F0.A.set(bit(a, 3))	# bit0 wordA
	F0.B.set(bit(b, 3))	# bit0 wordB
	F0.Cin.set(0)		# retenue_entrante
	F1.A.set(bit(a, 2))	# bit1 wordA
	F1.B.set(bit(b, 2))	# bit1 wordB
	F2.A.set(bit(a, 1))	# bit2 wordA
	F2.B.set(bit(b, 1))	# bit2 wordB
	F3.A.set(bit(a, 0))	# bit3 wordA
	F3.B.set(bit(b, 0))	# bit3 wordB
	# affichage des valeurs de sortie
	print('%i%i%i%i%i' %(int(F3.Cout.value), int(F3.S.value), int(F2.S.value), 					 int(F1.S.value), int(F0.S.value)))

#================================= PROGRAMME =================================#

from time import sleep

if __name__ == '__main__':
	#~ # l'horloge est une simple entrée, déclarée ici
	_clock_ = Plug('_clock_')
	# mais elle est simulée dans un thread dédié
	bgClockThread = ClockThread(_clock_); bgClockThread.start()
	# ce qui laisse la LDC libre pour toute création
	AND = AndGate('AND0')	# on créé une porte AND
	AND.A.set(1)			# on positionne son entrée A à 1
	_clock_.connect(AND.B)	# et on connecte l'horloge à son entrée B
	sleep(bgClockThread.spd)# on attends un tic d'horloge
	print(AND.O.value)		# et on imprime la sortie C de la porte AND
	time.sleep(1)			# on attends un second batement d'horloge
	print(AND.O.value)		# la sortie C a changée en fonction de l'horloge
	time.sleep(1)			# on attends encore un troisième tic
	print(AND.O.value)		# la sortie C est éguale à la valeur de l'horloge
							# ce qui est logique: 1 ET 0 = 0 / 1 ET 1 = 1
	bgClockThread.stop()	# enfin, on quite le thread de l'horloge
	
	adder_2x4('1011', '0010')
	HA1 = HalfAdder('HA1')
	
	print('_____________________________________________________\n')
	print('nbTopCircuits: %i' % (nbTopCircuits()))
	print('totalNbCircuits: %i' % (totalNbCircuits()))
	print('totalNbPlugs: %i' % totalNbPlugs())
	print('_____________________________________________________\n')
	printComponents(AND)
	print('_____________________________________________________\n')
	print(AND.plugList[0])


	
	

