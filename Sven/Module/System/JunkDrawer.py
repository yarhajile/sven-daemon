"""
Copyright (C) 2014, Web Bender Consulting, LLC. - All Rights Reserved
Unauthorized copying of this file, via any medium is strictly prohibited
Proprietary and confidential
Written by Elijah Ethun <elijahe@gmail.com>
"""

import time

from datetime import *
from Sven.Module.System.Base import Base
from Sven.Conditions import Conditions, ConditionValues
from Sven.Methods import *


class JunkDrawer(Base):
  current_timestamp = None
  current_time = None
  current_hour = None
  current_minute = None
  current_date = None
  current_day_of_week = None
  current_day_of_month = None
  current_month = None
  current_year = None
  current_date_time = None

  direction = 'out'


  class Meta(Meta):
    """
    Provides details about this module.
    """
    name = 'Common'
    description = 'System wide actions & conditions'


  def threadTarget(self, thread):

    """
    This method is the thread 'target' called from the parent addThread()
    method. The parent addThread() method is typically called from our static
    dispatch method.
    """

    notice("    JunkDrawer threadTarget initialized")

    while thread.running == True:
      if self.event_triggered is not None:
        self.runTriggeredEvents()

      self.runTimedUpdates(thread)

      self.current_timestamp = int(time.time())
      self.current_time = datetime.datetime.fromtimestamp(
        self.current_timestamp).strftime('%H:%M')
      self.current_hour = datetime.datetime.fromtimestamp(
        self.current_timestamp).strftime('%H')
      self.current_minute = datetime.datetime.fromtimestamp(
        self.current_timestamp).strftime('%M')
      self.current_date = datetime.datetime.fromtimestamp(
        self.current_timestamp).strftime('%Y-%m-%d')
      self.current_day_of_week = datetime.datetime.fromtimestamp(
        self.current_timestamp).strftime('%A')
      self.current_day_of_month = datetime.datetime.fromtimestamp(
        self.current_timestamp).strftime('%D')
      self.current_month = datetime.datetime.fromtimestamp(
        self.current_timestamp).strftime('%m')
      self.current_year = datetime.datetime.fromtimestamp(
        self.current_timestamp).strftime('%Y')
      self.current_date_time = '%s %s' \
                               % (self.current_date, self.self.currentTimestamp)

      time.sleep(2)


  def setOutputActionConditions(self):
    self.output_action_conditions = Conditions()

    self.output_action_conditions.add(
      key = 'current_time',
      type = 'time',
      multiple = False,
      name = 'Current Time',
      description = 'Current Time',
      predicates = ['all'])

    self.output_action_conditions.add(
      key = 'current_date',
      type = 'date',
      multiple = False,
      name = 'Current Date',
      description = 'Current Date',
      predicates = ['all'])

    self.output_action_conditions.add(
      key = 'current_date_time',
      type = 'datetime',
      multiple = False,
      name = 'Current Date & Time',
      description = 'Current Date & Time',
      predicates = ['all'])

    days_of_week = ConditionValues()
    days_of_week.add(value = 'Sunday', name = 'Sunday')
    days_of_week.add(value = 'Monday', name = 'Monday')
    days_of_week.add(value = 'Tuesday', name = 'Tuesday')
    days_of_week.add(value = 'Wednesday', name = 'Wednesday')
    days_of_week.add(value = 'Thursday', name = 'Thursday')
    days_of_week.add(value = 'Friday', name = 'Friday')
    days_of_week.add(value = 'Saturday', name = 'Saturday')

    self.output_action_conditions.add(
      key = 'current_day',
      type = 'list',
      multiple = True,
      name = 'Day of week',
      description = 'Day of week',
      values = days_of_week, predicates = ['all'])

    months = ConditionValues()
    months.add(value = '01', name = 'January')
    months.add(value = '02', name = 'February')
    months.add(value = '03', name = 'March')
    months.add(value = '04', name = 'April')
    months.add(value = '05', name = 'May')
    months.add(value = '06', name = 'June')
    months.add(value = '07', name = 'July')
    months.add(value = '08', name = 'August')
    months.add(value = '09', name = 'September')
    months.add(value = '10', name = 'October')
    months.add(value = '11', name = 'November')
    months.add(value = '12', name = 'December')

    self.output_action_conditions.add(
      key = 'current_mMonth', type = 'dict',
      multiple = True,
      name = 'Month',
      values = months,
      predicates = ['all'])


  class action_JunkDrawerAction(object):
    class Meta(Meta):
      name = 'JunkDrawer Action Name'
      description = 'JunkDrawer Action Description'

    def run(self, outer, *args, **kwargs):
      """
      Perform a productive output action
      """
