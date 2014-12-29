"""
Copyright (C) 2014, Web Bender Consulting, LLC. - All Rights Reserved
Unauthorized copying of this file, via any medium is strictly prohibited
Proprietary and confidential
Written by Elijah Ethun <elijahe@gmail.com>
"""

from Sven.Methods import *

class RCSwitchDevice():

  # Don't allow the module factory to execute us as we are handled only through 
  # RCSwitch.
  module_factory_ignore = True
  module_parameters = ['address', 'unitcode']
  required_parameters = ['address', 'unitcode']


  class Meta(Meta):
    name = 'Wireless Switches'
    description = 'Wireless 433mhz RC devices'


  @classmethod
  def dispatch(cls, module_factory, db, rcswitch, device_id = None):
    """
    Create list of module devices
    """

    notice("\n\tDispatching unit codes for switch address %s" % 
           rcswitch.address)

    if device_id is not None:
      cursor = db.execute("SELECT * FROM devices_rcswitch WHERE device_id = %s",
                          (device_id,))
    else:
      cursor = db.execute("SELECT * FROM devices_rcswitch "
                          "WHERE location_group_active = true "
                          "AND location_active = true "
                          "AND device_active = true AND address = %s",
        (str(rcswitch.address),))

    values = cursor.fetchall()

    objects = []

    for value in values:
      try:
        notice("\tDispatching unit code: %s for '%s' in '%s' at '%s'" %
               (value['unitcode'], value['device_name'], value['location_name'],
                value['location_group_name']))

        objects.append(RCSwitchDevice(module_factory = module_factory, db = db,
                                      id = value['device_id']))
      except:
        notice(traceback.format_exc())

    return objects