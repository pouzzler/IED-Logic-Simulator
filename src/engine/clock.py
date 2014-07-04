#!/usr/bin/env python3
# coding: utf-8

"""
############################################
##  thread dedicated to clock simulation  ##
############################################

With this module it's possible to create a plug which acts as the CPU clock.
This plug is an output whose value changes at regular intervals.
It's easy to connect this output to inputs so that they force the evaluation
of the circuit at each clock tick.
"""

from .circuits import *
from threading import Thread
import time


class ClockThread(Thread):
    """Launch this thread to simulate the clock.
    Use .connect([Plugs]) to connect the clock to other Plugs.
    """
    def __init__(self, clockPlug):
        Thread.__init__(self)
        self.clock = clockPlug     # clock plug
        self.alive = True          # the clock is running
        self.paused = False        # you can pause the clock
        self.spd = 1               # clock speed (sec)
        self.printFront = False    # specifies whether to display the clock

    def run(self):
        """Simulate the job of the clock.
        Allowing you to pause, unpause it and change its speed.
        """
        while self.alive:
            while self.paused:
                time.sleep(0.5)
            self.clock.set(not self.clock.value)
            if self.printFront:
                print(self.clock.value)
            time.sleep(self.spd)

    def pause(self):
        """Pause the clock."""
        self.paused = True

    def unpause(self):
        """Unpause the clock."""
        self.paused = False

    def stop(self):
        """Stop the clock."""
        self.alive = False

    def speed(self, sec):
        """"Set the clock speed (sec).""""
        self.spd = sec
