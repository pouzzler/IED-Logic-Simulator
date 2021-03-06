#!/usr/bin/env python3
# coding: utf-8


###############################################################################
#         ╔╦╗┌─┐┌─┐┬┌─┐  ╔═╗┬┬─┐┌─┐┬ ┬┬┌┬┐  ╔═╗┬┌┬┐┬ ┬┬  ┌─┐┌┬┐┌─┐┬─┐         #
#         ║║║├─┤│ ┬││    ║  │├┬┘│  │ ││ │   ╚═╗│││││ ││  ├─┤ │ │ │├┬┘         #
#         ╩ ╩┴ ┴└─┘┴└─┘  ╚═╝┴┴└─└─┘└─┘┴ ┴   ╚═╝┴┴ ┴└─┘┴─┘┴ ┴ ┴ └─┘┴└─         #
# -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+- #
#                                                                        2014 #
#                                                           Sébastien MAGNIEN #
#                                                            Mathieu FOURCROY #
# --------------------------------------------------------------------------- #
# With this module it's possible to create a plug which acts as the CPU clock.#
# This plug is an input whose value changes at regular intervals.             #
# It's easy to connect this input to inputs so that they force the evaluation #
# of the circuit at each clock tick.                                          #
###############################################################################


from threading import Thread
from .simulator import Plug
import time


class Clock(Plug):
    """A clock-ready Plug."""
    def __init__(self, owner):
        Plug.__init__(self, True, None, owner)
        self.clkThread = ClockThread(self)
        self.clkThread.start()
        self.clkThread.pause()


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
        self.externFun = None

    def run(self):
        """Simulate the job of the clock.
        Allowing you to pause, unpause it and change its speed.
        """
        while self.alive:
            while self.paused:
                time.sleep(0.5)
            self.clock.set(not self.clock.value)
            if self.externFun:
                self.externFun()
            time.sleep(self.spd)

    def set_extern(self, fun):
        """Set an external function to be run at each clock tic."""
        self.externFun = fun

    def pause(self):
        """Pause the clock."""
        self.paused = True

    def unpause(self):
        """Unpause the clock."""
        self.paused = False

    def stop(self):
        """Stop the clock."""
        self.alive = False

    def setSpeed(self, sec):
        """Set the clock speed (sec)."""
        self.spd = sec
