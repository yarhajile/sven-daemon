"""
Copyright (C) 2014, Web Bender Consulting, LLC. - All Rights Reserved
Unauthorized copying of this file, via any medium is strictly prohibited
Proprietary and confidential
Written by Elijah Ethun <elijahe@gmail.com>
"""
import RPi.GPIO

from Sven.Module.ModuleBase import ModuleBase
from Sven.Methods import *


class Base(ModuleBase):
  class InterfaceMeta(InterfaceMeta):
    name = 'Raspberry Pi'
    description = 'Interfacing with the Raspberry Pi'


  def parameterCheck(self):
    # Check basic values common to all modules first.
    super(Base, self).parameterCheck()

    # Check RaspberryPi specific parameters now.
    for parameter in self.device_parameters:
      name = parameter['parameter']
      value = parameter['value']

      # Direction check.
      if name == 'direction':
        if value not in ['in', 'out']:
          raise Exception(
            "GPIO direction must be either 'in' or 'out': %s given")

      # Edge check.
      # Check for RPi.GPIO.RISING, RPi.GPIO.FALLING or RPi.GPIO.BOTH.
      elif name == 'edge':
        if value in ['rising', RPi.GPIO.RISING]:
          setattr(self, 'edge', RPi.GPIO.RISING)

        elif value in ['falling', RPi.GPIO.FALLING]:
          setattr(self, 'edge', RPi.GPIO.FALLING)

        elif value in ['both', RPi.GPIO.BOTH]:
          setattr(self, 'edge', RPi.GPIO.BOTH)

        # Make sure the edge is either rising, falling or both.
        if self.edge not in [RPi.GPIO.RISING, RPi.GPIO.FALLING, RPi.GPIO.BOTH]:
          raise Exception(
            "Edge must be either 'rising', 'falling' or 'both': '%s given" % (
            value ))

      # Pull up / down resistor state.
      # Check for AdaBBIO.PUD_UP, AdaBBIO.PUD_DOWN or AdaBBIO.PUD_OFF
      elif name == 'pud':
        if value in [None, 'up', RPi.GPIO.PUD_UP]:
          setattr(self, 'pud', RPi.GPIO.PUD_UP)

        elif value in ['down', RPi.GPIO.PUD_DOWN]:
          setattr(self, 'pud', RPi.GPIO.PUD_DOWN)

        elif value in ['off', RPi.GPIO.PUD_OFF]:
          setattr(self, 'pud', RPi.GPIO.PUD_OFF)

        if self.pud not in [RPi.GPIO.PUD_UP, RPi.GPIO.PUD_DOWN,
                            RPi.GPIO.PUD_OFF]:
          raise Exception(
            "Invalid value for pull_up_down - should be either 'up', 'down' or "
            "'off': '%s' given" %
            (value))

      # Bouncetime check, convert to int
      elif name == 'bouncetime':
        try:
          value = int(value)
        except ValueError:
          pass

        setattr(self, 'bouncetime', value)


    # Make sure that the passed in device id has all required device parameters
    # to build this object for use
    for required_parameter in self.required_parameters:
      if not hasattr(self, required_parameter):
        raise Exception("'%s' required, but not found in %s object creation" %
                        (required_parameter, self.__class__.__name__ ))
