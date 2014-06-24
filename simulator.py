##########################################################################
## tente de simuler les portes et circuits logiques en python, sans GUI ##
##########################################################################

from comod import _INPT_
from comod import _OUPT_

# liste des circuits définies par l'utilisateur
topCircuits = []

# classe des connecteurs
# un connecteurs est une entrée ou une sortie
# les sorties se connectent sur les entrées
# donc si l'instance est une entrée elle n'aura pas d'items dans connections
class Plug:
	def __init__(self, name, owner=None, ptype=_OUPT_, printval=False):
		self.owner = owner		# circuit ou porte disposant de cette E/S
		self.name = name		# son nom
		self.ptype = ptype		# indique s'il faut réévaluer les valeurs
		self.printval = printval# indique s'il faut afficher sa valeur
		self.value = False		# au départ pas de courant
		self.nbEval = 0			# nombre de fois évalué
		self.connections = []	# entrées connectées si instance est une sortie
		if self.owner:			# ajoute le plug à la liste des plugs du circuit
			self.owner.addPlug(self)
			print('  %s add to %s plugs list' % (self.name, self.owner.name,))
	
	# usage: SORTIE.connect([ENTRÉE_A, ENTRÉE_B, ..., ENTRÉE_N])
	def connect(self, inputs):
		if not isinstance(inputs, list): inputs = [inputs] # transforme en liste
		for input in inputs: self.connections.append(input)# ajoute les connex°
	
	# usage: ENTRÉE.set([0/1])
	def set(self, value):
		if self.value == value and self.nbEval != 0:
			return							# la valeur n'a pas changé
		else:
			self.value = bool(value)		# sinon positionne la nouvelle
			self.nbEval += 1
		if self.ptype: self.owner.evalfun()	# réévaluer le circuit ?
		if self.printval:					# afficher la valeur ?
			print('%s.%s: %i' % (self.owner.name, self.name, int(self.value)))
		for connection in self.connections:	# change la valeur de toutes les
			connection.set(value)			# entrées connectées à cette sortie

# pour les circuits logiques
class Circuit:
	def __init__(self, name, owner=None):
		self.owner = owner
		self.name = name
		self.plugList = []
		self.circuitList = []
		if self.owner:			# ajoute le circ à la liste des circs du circuit
			self.owner.addCircuit(self)
			print('%s add to %s circuits list' % (self.name, self.owner.name,))
		else:
			topCircuits.append(self)
			print('%s add to topCircuits' % (self.name,))
	
	def evalfun(self):
		return
	
	def addPlug(self, plug):
		self.plugList.append(plug)
	
	def addCircuit(self, circuit):
		self.circuitList.append(circuit)
	
	def nbPlugs(self):
		return len(self.plugList)
	
	def nbCircuits(self):
		return len(self.circuitList)

# affiche les connecteurs d'un circuit et des circuits qui le constitue
def printComponents(circuit, verbose=True, indent=''):
	print(indent + '[' + circuit.name + ']')
	for plug in circuit.plugList:
		print(indent + '~~ ' + plug.name, end='')
		if verbose: print('\tTrue' if plug.value else '\tFalse')
		else: print('')
	for circuit in circuit.circuitList:
		printComponents(circuit, verbose, indent + '~~')

# calcule le nombre de connecteurs dans une liste de circuits
def countPlugs(circList):
	c = 0
	for circuit in circList:
		c += circuit.nbPlugs()
		c += countPlugs(circuit.circuitList)
	return c

# calcule le nombre total de connecteurs utilisés
def totalNbPlugs():
	return countPlugs(topCircuits)

# calcule le nombre de circuits dans une liste de circuits
# incluant les sous-circuits utilisés dans les circuits de la liste
def countCircuits(circList):
	c = 0
	for circuit in circList:
		c += 1
		c += countCircuits(circuit.circuitList)
	return c

# calcule le nombre total de circuits utilisés
def totalNbCircuits():
	return countCircuits(topCircuits)

# calcule le nombre de circuit définis par l'utilisateur
def nbTopCircuits():
	return len(topCircuits)

	

