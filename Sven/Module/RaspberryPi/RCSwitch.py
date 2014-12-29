"""
Copyright (C) 2014, Web Bender Consulting, LLC. - All Rights Reserved
Unauthorized copying of this file, via any medium is strictly prohibited
Proprietary and confidential
Written by Elijah Ethun <elijahe@gmail.com>
"""

import ctypes
from Sven.Module.RaspberryPi.Base import Base
from Sven.Module.RaspberryPi.RCSwitchDevice import RCSwitchDevice
from Sven.Methods import *


class RCSwitch(Base):
  module_parameters = ['address', 'unitcode', 'direction']
  required_parameters = ['address', 'unitcode', 'direction']


  class Meta(Meta):
    name = 'Wireless Switches'
    description = 'Wireless 433mhz RC devices'


  def threadTarget(self, thread):
    """
    This method is the thread 'target' called from the parent addThread()
    method. The parent addThread() method is typically called from our static
    dispatch method.
    """

    # Fetch list of unitcodes we'll be listening for on this address using
    # librcswitch.so.
    dll = ctypes.CDLL("/usr/lib/librcswitch.so")
    dll.initialize_rcswitch()

    self.address = int(self.address)

    if self.direction == 'in':
      dll.init_receiver(self.address)
      notice("\tRCSwitch receiver initialized on %s" % self.address)
    else:
      dll.init_transmitter(self.address)
      notice("\tRCSwitch transmitter initialized on %s" % self.address)

    last_execution_time = time.time()
    last_received_value = None

    while thread.running == True:
      #
      # Were we instructed by another thread to perform actions?
      #

      if self.event_triggered is not None:
        notice("Running triggered events from main thread loop")
        self.runTriggeredEvents()

      # Execute any updates prior to running our main code in order to rebuild
      # the thread with new values, if necessary.
      self.runTimedUpdates(thread)

      value = int(dll.get_received_value())

      if value > 0:
        valueFound = False

        # todo Occasionally, a switch will send different codes in a batch
        # like 54321, 54321, 65564, 54321.
        # The 65564 code is erronous and not picked up as we don't have a device
        # associated with it, however, in this case, device.callback() could be
        # called more than once in the 3 second static bounce time we specified.
        # Modifify this logic to account for that bug.
        for device in self.devices:
          if int(device.unitcode) == value:
            valueFound = True

            # same code received in less than 3 seconds
            if last_received_value != value or last_execution_time < time.time()-3:
              last_execution_time = time.time()
              last_received_value = value

              device.callback()

              data = {
                'id' : device.id,
                'address' : device.address,
                'unitcode' : device.unitcode,
                'name' : device.device_name,
                'location' : device.location_name,
                'location_group' : device.location_group_name,
                'time' : last_execution_time
              }

              self.getWebSocketServer().broadcastMessage(
                data = data,
                callback = 'RCSwitchTriggered',
                message = '')

        if valueFound == False:
          # Buffer notifications at 3 seconds
          if last_received_value != value or last_execution_time < time.time() - 3:
            self.eventDetected("Unknown unitcode: %s" % value)
            notice("Unknown unitcode discovered: %s" % value)
            last_execution_time = time.time()
            last_received_value = value

            # Tell the front-end that we see something
            self.getWebSocketServer().broadcastMessage(
              data = {
                'unitcode' : value,
                'time' : last_execution_time
              },
              callback = 'UnitCodeDiscovered', message = '')

      time.sleep(.03)


  @staticmethod
  def dispatch(module_factory, db, _temp, **kwargs):
    """
    Add RCSwitch threads.
    """

    if 'input_address' in kwargs and 'input_unitcode' in kwargs:
      device_exists = False

      items = module_factory.dispatched_modules.modules.items()
      for module_name, module_items in items:
        for device in module_items:
          if device.__class__.__name__ == 'RCSwitch' \
             and str(device.address) == str(kwargs['input_address']):
            # extend new RCSwitchDevice to device.devices.
            device_exists = True
            device.devices.extend(RCSwitchDevice.dispatch(module_factory, db,
                                                          device,
                                                          kwargs['device_id']))

      if device_exists == False:
        # The supplied 'address' does not yet exist in the dispatched modules
        # list, create a new RCSwitch instance and accompanying RCSwitchDevice
        # child.
        try:
          object = RCSwitch(module_factory = module_factory, db = db,
                            id = kwargs['device_id'])

          # Add the devices that will contain the unitcodes and accompanying
          # callback methods to the object.
          object.devices = RCSwitchDevice.dispatch(module_factory, db, object)

          # Hand it off to the thread handler
          object.addThread()

        except:
          notice(traceback.format_exc())
      return

    cursor = db.execute("SELECT DISTINCT ON (address) * FROM devices_rcswitch "
                        "WHERE location_group_active = true "
                        "AND location_active = true AND device_active = true")
    values = cursor.fetchall()

    for value in values:
      try:
        object = RCSwitch(module_factory = module_factory, db = db,
                          id = value['device_id'])

        # Add the devices that will contain the unitcodes and accompanying
        # callback methods to the object.
        object.devices = RCSwitchDevice.dispatch(module_factory, db, object)

        # Hand it off to the thread handler
        object.addThread()

      except:
        notice(traceback.format_exc())
