############################################
##  thread dedicated to clock simulation  ##
############################################

from .circuits import *
from threading import Thread
import time


# launch this thread to simulate the clock
# use .connect([[Plugs]]) to connect the clock to other Plugs
class ClockThread(Thread):
    def __init__(self, clockPlug):
        Thread.__init__(self)
        self.clock = clockPlug     # clock plug
        self.alive = True          # the clock is running
        self.paused = False        # you can pause the clock
        self.spd = 1               # clock speed (sec)
        self.printFront = False    # specifies whether to display the clock

    # simulate the job of the clock
    # allowing you to pause, unpause it and change its speed
    def run(self):
        while self.alive:
            while self.paused:
                time.sleep(0.5)
            self.clock.set(not self.clock.value)
            if self.printFront:
                print(self.clock.value)
            time.sleep(self.spd)

    # pause the clock
    def pause(self):
        self.paused = True

    # unpause the clock
    def unpause(self):
        self.paused = False

    # stop the clock
    def stop(self):
        self.alive = False

    # set the clock speed (sec)
    def speed(self, sec):
        self.spd = sec
