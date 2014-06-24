####################################################################
##              portes logiques de base: NON, OU, ET              ##
## ces portes permettent de sontruire des circuits plus complexes ##
##             circuits.py contient quelques exemples             ##
##      user_circuits contient ceux définis par l'utilisateur     ##
####################################################################

from comod import _INPT_
from comod import _OUPT_
from simulator import *

# porte NOT: O = NON A
class NotGate(Circuit):
	def __init__(self, name, owner=None):
		Circuit.__init__(self, name, owner)
		# E/S du circ	nom		proprio	E/S		affichage
		self.A = Plug( 	'A', 	self, 	_INPT_, False)	# i: bitA
		self.O = Plug( 	'O', 	self,	_OUPT_,	False)	# o: NOT bitA
	def evalfun(self): self.O.set(not self.A.value)

# porte AND: O = A ET B
class AndGate(Circuit):
	def __init__(self, name, owner=None, inputs=['A', 'B']):
		if 'O' in inputs: return	# O est déjà utilisé
		Circuit.__init__(self, name, owner)
		self.inputList = []			# liste des entrées
		for inp in inputs:			# génère les entrée et ajoute-les à la liste
			exec("self.%s = Plug('%s', self, _INPT_)" % (inp, inp,))
			exec('self.inputList.append(self.%s)' % (inp,))
		self.O = Plug( 	'O', 	self,	_OUPT_,	False)
	def evalfun(self):				# ET logique de toutes les entrées
		out = True
		for inp in self.inputList:
			if inp.value == False: out = False; break
		self.O.set(out)

# porte OR: O = A OU B
class OrGate(Circuit):
	def __init__(self, name, owner=None, inputs=['A', 'B']):
		if 'O' in inputs: return	# O est déjà utilisé
		Circuit.__init__(self, name, owner)
		self.inputList = []			# liste des entrées
		for inp in inputs:			# génère les entrée et ajoute-les à la liste
			exec("self.%s = Plug('%s', self, _INPT_)" % (inp, inp,))
			exec('self.inputList.append(self.%s)' % (inp,))
		self.O = Plug( 	'O', 	self,	_OUPT_,	False)
	def evalfun(self):
		out = False
		for inp in self.inputList:
			if inp.value == True: out = True; break
		self.O.set(out)

# porte XOR: O = A OU-EXCLUSIF B
class XorGate(Circuit):
	def __init__(self, name, owner=None, inputs=['A', 'B']):
		if 'O' in inputs: return	# O est déjà utilisé
		Circuit.__init__(self, name, owner)
		self.inputList = []			# liste des entrées
		for inp in inputs:			# génère les entrée et ajoute-les à la liste
			exec("self.%s = Plug('%s', self, _INPT_)" % (inp, inp,))
			exec('self.inputList.append(self.%s)' % (inp,))
		self.O = Plug( 	'O', 	self,	_OUPT_,	False)
	def evalfun(self):
		c = 0
		for inp in self.inputList:
			if inp.value == True: c += 1
		self.O.set(c%2)

# porte NAND: O = NON (A ET B)
class NandGate(Circuit):
	def __init__(self, name, owner=None, inputs=['A', 'B']):
		if 'O' in inputs: return	# O est déjà utilisé
		Circuit.__init__(self, name, owner)
		self.inputList = []			# liste des entrées
		for inp in inputs:			# génère les entrée et ajoute-les à la liste
			exec("self.%s = Plug('%s', self, _INPT_)" % (inp, inp,))
			exec('self.inputList.append(self.%s)' % (inp,))
		self.O = Plug( 	'O', 	self,	_OUPT_,	False)
	def evalfun(self):
		out = False
		for inp in self.inputList:
			if inp.value == False: out = True; break
		self.O.set(out)

