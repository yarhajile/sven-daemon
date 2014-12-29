"""
Copyright (C) 2014, Web Bender Consulting, LLC. - All Rights Reserved
Unauthorized copying of this file, via any medium is strictly prohibited
Proprietary and confidential
Written by Elijah Ethun <elijahe@gmail.com>
"""

from Sven.Module.Cloud.Nest import Nest
from Sven.Conditions import Conditions, ConditionValues
from Sven.Methods import *

class NestProtect(Nest) :
  module_parameters = ['nestaccount', 'serial', 'index']
  required_parameters = ['nestaccount', 'serial', 'index']

  module_factory_ignore = True


  def build(self, db):
    super(Nest, self).build(db)

    self.serial = '02AA01AC371305HK'

    # Set the parent to be the nestaccount id set in the front-end.
    self.parent = self.getDeviceById(self.nestaccount)


  class Meta(Meta):
    name = 'Nest Protect'


  def setOutputActionConditions(self) :
    self.output_action_conditions = Conditions()


  def threadTarget(self, thread) :

    """
    This method is the thread 'target' called from the parent addThread()
    method. The parent addThread() method is typically called from our static
    dispatch method.
    """

    # Set to 10 minutes so that it runs on startup.  This will be set to 0 on
    # the first iteration. Add a 5 second delay to this so that the parent
    # process has enough time to retrieve and process the login token & status.
    update_timer = 600 - 5

    while thread.running == True:

      if self.event_triggered is not None:
        self.runTriggeredEvents()

      self.runTimedUpdates(thread)

      if update_timer >= 600:
        self.parent.setup(force_reload_status = True)
        # Do something now that 10 minutes has passed

        update_timer = 0

      # This timer business is so that when we stop the main process, we're not
      # stuck waiting for this long-run loop to finish.
      update_timer += .5
      time.sleep(1)


  @classmethod
  def dispatch(cls, module_factory, db, **kwargs):
    if 'device_id' in kwargs:
      try:
        object = NestProtect(module_factory = module_factory, db = db,
                             id = kwargs['device_id'])

        # Hand it off to the thread handler
        object.addThread()
      except :
        notice(traceback.format_exc())
      return

    cursor = db.execute("SELECT device_id FROM devices_NestProtect "
                        "WHERE location_group_active = true "
                        "AND location_active = true AND device_active = true")
    values = cursor.fetchall()

    for value in values:
      try:
        object = NestProtect(module_factory = module_factory, db = db,
                             id = value['device_id'])

        # Hand it off to the thread handler
        object.addThread()
      except :
        notice(traceback.format_exc())


  def geDeviceInfo(self):
    protect = self.status['topaz'][self.serial]

    return {
      'name' : getattr(protect, protect['description'], 'Not Set'),
      'where' : self.getWhere(protect['spoken_where_id']),
      'serial_number' : protect['serial_number'],
      'location' : protect['structure_id'],
      'co_status' : protect['co_status'],
      'smoke_status' : protect['smoke_status'],
      'line_power_present' : protect['line_power_present'],
      'battery_level' : protect['battery_level'],
      'battery_health_state' : protect['battery_health_state'],
      'replace_by_date' : protect['replace_by_date_utc_secs'],
      'last_update' : protect['timestamp'],
      'last_manual_test' : protect['latest_manual_test_start_utc_secs'],
      'tests_passed' : {
        'led' : protect['component_led_test_passed'],
        'pir' : protect['component_pir_test_passed'],
        'temp' : protect['component_temp_test_passed'],
        'smoke' : protect['component_smoke_test_passed'],
        'heat' : protect['component_heat_test_passed'],
        'wifi' : protect['component_wifi_test_passed'],
        'als' : protect['component_als_test_passed'],
        'co' : protect['component_co_test_passed'],
        'us' : protect['component_us_test_passed'],
        'hum' : protect['component_hum_test_passed']
      },
      'network' : {
        'online' : protect['component_wifi_test_passed'],
        'local_ip' : protect['wifi_ip_address'],
        'mac_address' : protect['wifi_mac_address']
      }
    }
