IED Logic Simulator
===================

La racine du repositoire contient quelques fichiers tels que :

* CDC.pdf , le cahier des charges de notre simulateur de circuits logiques,
* README.md , le fichier présent,
* LICENCE , la licence sous laquelle tous ces fichiers sont proposés.

Le contenu principal est lui dans le sous-dossier /src :

* /src/main.py , le programme principal

* /src/engine contenant le moteur de simulation, <à décrire par Mathieu>

* /src/gui contenant l'interface utilisateur graphique :
  
  * /src/gui/mainWindow.py est la fenêtre principale du programme.
  
  * /src/gui/mainView.py : une zone de travail dans laquelle l'utilisateur
  glisse et dépose des éléments de circuit logique afin d'en bâtir de plus
  complexes.
  
  * /src/gui/toolBox.py : une "boite à outil" dockable contenant des 
  éléments de circuit logique à utiliser dans la zone de travail.
  
  * /src/gui/toolOptions.py : une zone permettant de changer les options
  des éléments sélectionnés, en particulier leur nombre d'entrées.
  
  * /src/gui/circuit.py : une classe permettant de représenter un circuit
  sous forme d'objet graphique dans la zone de travail tout en assurant
  le lien avec le moteur de simulation.
  



