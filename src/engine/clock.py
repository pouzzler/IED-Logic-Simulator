##############################################################################
# thread pour l'horloge permetant de simuler l'horloge dans un thread séparé #
##############################################################################

from .circuits import *
from threading import Thread
import time


# thread à lancer pour simuler une horloge
# utiliser .connect([[Plugs]]) pour connecter l'horloge à des connecteurs
class ClockThread(Thread):
    def __init__(self, clockPlug):
        Thread.__init__(self)
        self.clock = clockPlug     # connecteur horloge
        self.alive = True          # ça tourne !
        self.paused = False        # pour mettre l'horloge en pause
        self.spd = 1               # la vitesse de l'horloge (en secondes)
        self.printFront = False    # indique s'il faut afficher l'horloge

    # fait tourner l'horloge
    # et permet de la mettre en pause et de changer sa vitesse
    def run(self):
        while self.alive:
            while self.paused:
                time.sleep(0.5)
            self.clock.set(not self.clock.value)
            if self.printFront:
                print(self.clock.value)
            time.sleep(self.spd)

    # mettre en pause
    def pause(self):
        self.paused = True

    # reprendre
    def unpause(self):
        self.paused = False

    # arrêter
    def stop(self):
        self.alive = False

    # changer la vitesse (en sec)
    def speed(self, sec):
        self.spd = sec
