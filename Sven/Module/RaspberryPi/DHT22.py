"""
Copyright (C) 2014, Web Bender Consulting, LLC. - All Rights Reserved
Unauthorized copying of this file, via any medium is strictly prohibited
Proprietary and confidential
Written by Elijah Ethun <elijahe@gmail.com>
"""

import Sven.dhtreader

from Sven.Methods import *
from Sven.Module.RaspberryPi.Base import Base

class DHT22(Base):
  module_parameters = ['address']
  required_parameters = ['address']


  class Meta(Meta):
    name = 'Humidity / Temperature sensor'


  def threadTarget(self, thread):
    """
    This method is the thread 'target' called from the parent addThread()
    method. The parent addThread() method is typically called from our static
    dispatch method.
    """

    type = 22
    pin = 25

    dhtreader.init()

    self.address = int(self.address)

    while thread.running == True:
      #
      # Were we instructed by another thread to perform actions?
      #
      if self.event_triggered is not None:
        self.runTriggeredEvents()

      # Execute any updates prior to running our main code in order to rebuild
      # the thread with new values, if necessary.
      self.runTimedUpdates(thread)

      # 22 is the code for the DHT22 sensor
      value = dhtreader.read(self.type, self.address)

      if value == 'None':
        time.sleep(3)
        continue

      value = value.replace("(", "")
      value = value.replace(")", "")
      value = value.replace(" ", "")

      values = value.split(',')

      self.current_temperature = values[0]
      self.current_humidity = values[1]

      time.sleep(5)
