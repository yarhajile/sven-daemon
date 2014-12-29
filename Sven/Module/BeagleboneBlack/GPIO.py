"""
Copyright (C) 2014, Web Bender Consulting, LLC. - All Rights Reserved
Unauthorized copying of this file, via any medium is strictly prohibited
Proprietary and confidential
Written by Elijah Ethun <elijahe@gmail.com>
"""

import Adafruit_BBIO.GPIO as AdaGPIO

from Sven.Module.BeagleboneBlack.Base import Base
from Sven.Database import Database
from Sven.Methods import *


class GPIO(Base):
  module_parameters = ['address', 'bouncetime', 'direction', 'edge', 'pud']
  required_parameters = ['address', 'bouncetime', 'direction', 'edge', 'pud']

  class Meta(Meta):
    name = 'GPIO Module'
    description = 'Standard GPIO input / output'

  def addEvent(self):
    """
    Add add_event_detect to address.
    """

    # Add the event listener
    AdaGPIO.add_event_detect(self.address, self.edge,
                             callback = getattr(self, 'callback'),
                             bouncetime = self.bouncetime)
    notice("\tAdded event detection for %s" % self.address)

  def removeEvent(self):
    """
    Remove event detection.
    """

    if self.direction == 'in':
      AdaGPIO.remove_event_detect(self.address)
      notice("Removed GPIO event detection for %s" % self.address)

  def handleUpdates(self, thread):
    """
    Called every few seconds from the daemon monitor to perform updates to
    this thread.
    """

    # Setup a new database connection to be used in the handleUpdates
    # instance.
    db = Database.open(self.module_factory.config)

    update = super(GPIO, self).handleUpdates(thread, db)

    # Parent says that we have updates to process, rebuild the object
    if update == True and self.direction == 'in':
      try:
        # Add the event detection
        self.addEvent()
      except:
        # Something went wonky rebuilding the object or adding the event, go
        # tell mom & dad.
        notify(traceback.format_exc());

    db.close()


  def cleanup(self):
    """
    Cleanup method called from parent __del__ destructor.
    """

    AdaGPIO.cleanup()


  def threadTarget(self, thread):
    if self.direction == 'in':
      direction = AdaGPIO.IN
    else:
      direction = AdaGPIO.OUT

    # Setup the pin
    AdaGPIO.setup(self.address, direction, pull_up_down = self.pud)

    if self.direction == 'in':
      notice("\tDispatching 'input' event listener for GPIO address %s" %
             self.address)
      self.addEvent()
    else:
      notice("\tDispatching GPIO address %s as output" % self.address)

    while thread.running == True:
      if self.event_triggered is not None:
        self.runTriggeredEvents()

      self.runTimedUpdates(thread)
      time.sleep(.05)

  def blink(self, duration):
    AdaGPIO.output(self.address, AdaGPIO.HIGH)
    time.sleep(duration)
    AdaGPIO.output(self.address, AdaGPIO.LOW)


  #
  # Define actions we can perform when we are in an OUTPUT state.
  #
  class action_chirp(object):
    class Meta(Meta):
      name = 'Chirp'
      description = 'Chirps the output twice'


    def run(self, outer, *args, **kwargs):
      how_many = 2
      chirps = 0

      while chirps < how_many:
        outer.blink(.04)
        time.sleep(.04)
        chirps = chirps + 1

  class action_siren(object):
    class Meta(Meta):
      name = 'Siren'
      description = 'Woowoowoowoo!'

    def run(self, outer, *args, **kwargs):
      outer.blink(.5)


  class action_blink(object):
    class Meta(Meta):
      name = 'Blink'
      description = 'Flash output once'

    def run(self, outer, *args, **kwargs):
      how_many = 1
      blinks = 0

      while blinks < how_many:
        outer.blink(.5)

        time.sleep(.5)

        blinks = blinks + 1


  class action_sos(object):
    class Meta(Meta):
      name = 'SOS'
      description = 'Outputs ...---... twice'

    def run(self, outer, *args, **kwargs):
      how_many = 2
      blinks = 0

      while blinks < how_many:
        outer.blink(.2)
        time.sleep(.2)
        outer.blink(.2)
        time.sleep(.2)
        outer.blink(.2)
        time.sleep(.4)

        outer.blink(.4)
        time.sleep(.4)
        outer.blink(.4)
        time.sleep(.4)
        outer.blink(.4)
        time.sleep(.4)

        outer.blink(.2)
        time.sleep(.2)
        outer.blink(.2)
        time.sleep(.2)
        outer.blink(.2)

        blinks = blinks + 1
        time.sleep(.5)
