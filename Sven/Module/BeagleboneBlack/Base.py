"""
Copyright (C) 2014, Web Bender Consulting, LLC. - All Rights Reserved
Unauthorized copying of this file, via any medium is strictly prohibited
Proprietary and confidential
Written by Elijah Ethun <elijahe@gmail.com>
"""

# Import the GPIO module, all we really want are the constants.  Maybe there's
# a better way to get these?
import Adafruit_BBIO.GPIO as AdaBBIO

from Sven.Module.ModuleBase import ModuleBase
from Sven.Methods import *


class Base(ModuleBase):
  class InterfaceMeta(InterfaceMeta):
    name = 'Beaglebone Black'
    description = 'Beaglebone Black Rev B'

  def parameterCheck(self):

    # Check basic values common to all modules first
    super(Base, self).parameterCheck()

    # Check BeagleboneBlack specific parameters now
    for parameter in self.device_parameters:
      name = parameter['parameter']
      value = parameter['value']

      # Direction check
      if name == 'direction':
        if value not in ['in', 'out']:
          raise Exception(
            "GPIO direction must be either 'in' or 'out' : %s given.")

      # Edge check
      # Check for AdaBBIO.RISING, AdaBBIO.FALLING or AdaBBIO.BOTH
      elif name == 'edge':
        if value in ['rising', AdaBBIO.RISING]:
          setattr(self, 'edge', AdaBBIO.RISING)

        elif value in ['falling', AdaBBIO.FALLING]:
          setattr(self, 'edge', AdaBBIO.FALLING)

        elif value in ['both', AdaBBIO.BOTH]:
          setattr(self, 'edge', AdaBBIO.BOTH)

        # Make sure the edge is either rising, falling or both
        if self.edge not in [AdaBBIO.RISING, AdaBBIO.FALLING, AdaBBIO.BOTH]:
          raise Exception(
            "Edge must be either 'rising', 'falling' or 'both' : '%s given." % (
            value ))

      # Pull up / down resistor state
      # Check for AdaBBIO.PUD_UP, AdaBBIO.PUD_DOWN or AdaBBIO.PUD_OFF
      elif name == 'pud':
        if value in [None, 'up', AdaBBIO.PUD_UP]:
          setattr(self, 'pud', AdaBBIO.PUD_UP)

        elif value in ['down', AdaBBIO.PUD_DOWN]:
          setattr(self, 'pud', AdaBBIO.PUD_DOWN)

        elif value in ['off', AdaBBIO.PUD_OFF]:
          setattr(self, 'pud', AdaBBIO.PUD_OFF)

        if self.pud not in [AdaBBIO.PUD_UP, AdaBBIO.PUD_DOWN, AdaBBIO.PUD_OFF]:
          raise Exception("Invalid value for pull_up_down - should be either "
                          "'up', 'down' or 'off': '%s' given." % (value))

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
        raise Exception("'%s' required, but not found in %s object creation." %
                        (required_parameter, self.__class__.__name__))
