"""
Copyright (C) 2014, Web Bender Consulting, LLC. - All Rights Reserved
Unauthorized copying of this file, via any medium is strictly prohibited
Proprietary and confidential
Written by Elijah Ethun <elijahe@gmail.com>
"""

import time
from Sven.Module.System.Base import Base
from Sven.Conditions import Conditions, ConditionValues
from Sven.Methods import *


class Alarm(Base):
  module_parameters = []
  current_state = None

  def __init__(self, module_factory = None, db = None, id = None):
    super(Alarm, self).__init__(module_factory, db, id)

  class Meta(Meta):
    """
    Provides details about this module.
    """
    name = 'Alarm System'


  def threadTarget(self, thread):
    while thread.running == True:
      if self.event_triggered is not None:
        self.runTriggeredEvents()

      self.runTimedUpdates(thread)

      time.sleep(.2)


  def setOutputActionConditions(self):
    self.output_action_conditions = Conditions()

    self.output_action_conditions.add(
      key = 'indoor_temp',
      type = 'float',
      multiple = False,
      name = 'Indoor Temperature',
      description = 'Indoor Temperature',
      predicates = ['lt', 'gt'])

    self.output_action_conditions.add(
      key = 'outdoor_temp',
      type = 'float',
      multiple = False,
      name = 'Outdoor Temperature',
      description = 'Outdoor Temperature',
      predicates = ['le', 'ge'])

    self.output_action_conditions.add(
      key = 'indoor_humidity',
      type = 'float',
      multiple = False,
      name = 'Outdoor Humidity',
      description = 'Outdoor Humidity',
      predicates = ['eq'])

    self.output_action_conditions.add(
      key = 'outdoor_humidity',
      type = 'float',
      multiple = False,
      name = 'Outdoor Humidity',
      description = 'Outdoor Humidity',
      predicates = ['ne'])

    hvac_modes = ConditionValues()
    hvac_modes.add(key = 'id', value = 1, name = 'Cool',
                  description = 'Air Conditioning Mode')
    hvac_modes.add(key = 'id', value = 2, name = 'Heat',
                  description = 'Heating Mode')
    hvac_modes.add(key = 'id', value = 3, name = 'Both',
                  description = 'Both Heat & Cool Mode')

    self.output_action_conditions.add(
      key = 'hvac_mode', type = 'dict',
      multiple = False,
      name = 'HVAC Mode',
      description = 'Heating & Air Conditioning Mode',
      values = hvac_modes,
      predicates = ['ne', 'gt', 'eq'])

  class action_GetStatus(object):
    class Meta(Meta):
      name = 'Get Alarm Status'

    def run(self, outer, *args, **kwargs):
      return outer.current_state

  class action_SetStatus(object):
    class Meta(Meta):
      name = 'Set Alarm Status'

    def run(self, outer, *args, **kwargs):
      outer.current_state = kwargs['state']
