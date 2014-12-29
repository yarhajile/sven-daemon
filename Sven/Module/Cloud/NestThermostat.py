"""
Copyright (C) 2014, Web Bender Consulting, LLC. - All Rights Reserved
Unauthorized copying of this file, via any medium is strictly prohibited
Proprietary and confidential
Written by Elijah Ethun <elijahe@gmail.com>
"""

import simplejson as json

from Sven.Methods import *
from Sven.Module.Cloud.Nest import Nest
from Sven.Conditions import Conditions, ConditionValues


class NestThermostat(Nest):
  module_parameters = ['nestaccount', 'units', 'serial']
  required_parameters = ['nestaccount', 'units', 'serial']

  module_factory_ignore = True

  def build(self, db):
    super(Nest, self).build(db)

    self.serial = '02AA01AC371305HK'
    self.direction = 'both'

    # Set the parent to be the nestaccount id set in the front-end.
    self.parent = self.getDeviceById(self.nestaccount)


  class Meta(Meta):
    name = 'Nest Learning Thermostat'
    description = 'Nest v2.0'


  def setOutputActionConditions(self):
    self.output_action_conditions = Conditions()

    self.output_action_conditions.add(
      key = 'indoor_temp', type = 'float',
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


  def threadTarget(self, thread):

    """
    This method is the thread 'target' called from the parent addThread()
    method. The parent addThread() method is typically called from our static
    dispatch method.
    """

    # Set to 10 minutes so that it runs on startup.  This will be set to 0 on
    # the first iteration. Add a 5 second delay to this so that the parent
    # process has enough time to retrieve and process the login token & status
    updateTimer = 600 - 5

    while thread.running == True:
      if self.event_triggered is not None:
        self.runTriggeredEvents()

      self.runTimedUpdates(thread)

      # Update the temp & humidity every 10 minutes.
      if updateTimer >= 600:
        self.parent.setup(force_reload_status = True)

        # Use the parents connection for the status we work with.
        self.status = self.parent.status

        self.temperature = self.currentTemperature()
        self.humidity = self.currentHumidity()

        self.getWebSocketServer().broadcastMessage(
          data = self.currentWeather(),
          callback = 'CurrentWeather',
          message = '')

        notice('Nest temperature: ' + str(self.temperature))
        notice('Nest Humidity: ' + str(self.humidity))

        updateTimer = 0

      # This timer business is so that when we stop the main process, we're not
      # stuck waiting for this long-run loop to finish.
      updateTimer += .5
      time.sleep(1)

  @classmethod
  def dispatch(cls, module_factory, db, **kwargs):
    if 'device_id' in kwargs:
      try:
        object = NestThermostat(module_factory = module_factory, db = db,
                                id = kwargs['device_id'])

        # Hand it off to the thread handler
        object.addThread()
      except:
        notice(traceback.format_exc())

      return

    cursor = db.execute("SELECT device_id FROM devices_NestThermostat "
                        "WHERE location_group_active = true "
                        "AND location_active = true AND device_active = true")
    values = cursor.fetchall()

    for value in values:
      try:
        object = NestThermostat(module_factory = module_factory, db = db,
                                id = value['device_id'])

        # Hand it off to the thread handler.
        object.addThread()
      except:
        notice(traceback.format_exc())


  def energyLatest(self):
    data = {
      'objects' : {
        'object_key' : "energy_latest." + self.serial}}

    return self.request.post(self.transport_url + "/v5/subscribe", 
                             data = data,
                             headers = self.parent.headers())


  def getDeviceInfo(self):
    shared = self.status['shared'][self.serial]
    device = self.status['device'][self.serial]
    structure = self.status['structure'][self.serial]

    mode = device['current_schedule_mode'].lower()
    manual_away = structure['away']
    target_mode = shared['target_temperature_type']

    if manual_away or mode == 'away' or shared['auto_away'] > 0:
      mode += ',away'
      target_mode = 'range'
      target_temperatures = (self.tempOutput(device['away_temperature_low']),
                            self.tempOutput(device['away_temperature_high']))
    elif mode == 'range':
      target_mode = 'range'
      target_temperatures = (self.tempOutput(shared['target_temperature_low']),
                            self.tempOutput(shared['target_temperature_high']))
    else:
      target_temperatures = self.tempOutput(shared['target_temperature'])

    output = {
      'current_state' : {
        'mode' : mode,
        'temperature' : self.currentTemperature(),
        'humidity' : self.currentHumidity(),
        'ac' : shared['hvac_state'],
        'heat' : shared['hvac_heater_state'],
        'alt_heat' : shared['hvac_alt_heat_state'],
        'fan' : shared['hvac_fan_state'],
        'auto_away' : shared['auto_away'],
        'manual_away' : manual_away,
        'leaf' : device['leaf'],
        'battery_level' : device['battery_level']
      },
      'target' : {
        'mode' : target_mode,
        'temperature' : target_temperatures,
        'time_to_target' : device['time_to_target'],

      },
      'serial_number' : device['serial_number'],
      'scale' : device['temperature_scale'],
      'location' : self.structure,
      'network' : self.getDeviceNetworkInfo(),
      'name' : getattr(shared, 'name', 'Not Set'),
      'where' : self.getWhere(device['where_id'])
    }

    if device['has_humidifier'] == True:
      output['current_state']['humidifier'] = device['humidifier_state']
      output['target']['humidity'] = device['target_humidity']
      output['target']['humidity_enabled'] = device['target_humidity_enabled']

    return output


  def getDeviceSchedule(self):
    scheduledDays = self.status['schedule'][self.serial]['days']

    schedule = {}

    for day, scheduledEvents in scheduledDays.iteritems():
      events = {}

      for scheduledEvent in scheduledEvents:
        if scheduledEvent['entry_type'] == 'setpoint':
          if scheduledEvent['type'] == 'RANGE':
            targetTemperature = (
              self.temperatureInUserScale(scheduledEvent['temp-min']),
              self.temperatureInUserScale(scheduledEvent['temp-max'])
            )
          else:
            targetTemperature = self.temperatureInUserScale(
              scheduledEvent['temp'])

          events[int(scheduledEvent['time'])] = {
            'time' : int(scheduledEvent['time']) / 60,
            'target_temperature' : targetTemperature,
            'mode' : scheduledEvent['type']
          }

      return events

  def getNextScheduledEvent(self):
    schedule = self.getDeviceSchedule()
    time_now = time.strftime('%H') * 60 + time.strftime('%i')

    i = 0
    day = datetime.today()

    while i < 7:
      if day in schedule:
        for event in schedule[day]:
          if event['time'] > time_now:
            return event
      i += 1
      day += datetime.timedelta(days = 1)

    return False


  def setTargetTemperatureMode(self, mode, temperature):
    data = {
      'target_change_pending' : True,
      'target_temperature_mode' : mode
    }

    if mode == 'range' :
      if not isinstance(temperature, tuple):
        raise Exception("When using 'range' mode, you need to set the target "
                        "temperatures using a tuple of (temperature_low, "
                        "temperature_high).")

      data['target_temperature_low'] = self.temperatureInCelcius(temperature[0])
      data['target_temperature_high'] = self.temperatureInCelcius(
        temperature[1])

    elif mode != 'off':
      if not isinstance(temperature, [int, basestring]):
        raise Exception("When using 'heat' or 'cool' modes, you need to set "
                        "the target temperature using a numeric value.")

      data['target_temperature'] = self.temperature_in_celsius(temperature)

    self.postPutShared(json.dumps(data))


  def setTargetTemperature(self, temperature):
    data = {
      'target_change_pending' : True,
      'target_temperature' : self.temperature_in_celsius(temperature)
    }

    self.postPutShared(json.dumps(data))


  def settarget_temperatures(self, temperature_low, temperature_high):
    data = {
      'target_change_pending' : True,
      'target_temperature_low' : self.temperature_in_celsius(temperature_low),
      'target_temperature_low' : self.temperature_in_celsius(temperature_high)
    }

    self.postPutShared(json.dumps(data))


  def setAwayTemperatures(self, temperature_low = None, temperature_high = None):
    data = {}

    if temperature_low is not None:
      temperature_low = self.temperature_in_celsius(temperature_low)

    if temperature_high is not None:
      temperature_high = self.temperature_in_celsius(temperature_high)

    if temperature_low is None or temperature_low < 4:
      data['away_temperature_low_enabled'] = False
    elif temperature_low is not None:
      data['away_temperature_low_enabled'] = True
      data['away_temperature_low'] = temperature_low

    if temperature_high is None or temperature_high > 32:
      data['away_temperature_high_enabled'] = False
    elif temperature_low is not None:
      data['away_temperature_high_enabled'] = True
      data['away_temperature_high'] = temperature_high

    self.postPutDevice(json.dumps(data))


  def _setFanMode(self, mode = None, duty_cycle = None, timer = None):
    data = {}

    if mode is not None:
      data['fan_mode'] = mode

    if duty_cycle is not None:
      data['fan_duty_cycle'] = int(duty_cycle)

    if timer is not None:
      data['fan_timer_duration'] = timer
      data['fan_timer_timeout'] = time.time() + timer

    self.postPutDevice(json.dumps(data))


  def setFanMode(self, mode_input):
    duty_cycle = None
    timer = None

    if isinstance(mode_input, tuple):
      mode = mode_input[0]
      if len(mode_input) > 1:
        if mode == 'duty-cycle':
          duty_cycle = int(mode_input[1])
        else:
          timer = int(mode_input[1])
      else:
        raise Exception("setFanMode( tuple() ) needs at least a mode and a "
                        "value in the mode tuple.")
    elif not isinstance(mode_input, basestring):
      raise Exception("setFanMode() can only take a string or a tuple as it's "
                      "parameter.")

    return self._setFanMode(mode, duty_cycle, timer)


  def setFanModeMinutesPerHour(self, **kwargs):
    return self._setFanMode(mode = kwargs['mode'],
                            duty_cycle = kwargs['duty_cycle'])


  def setFanModeMinutesPerHour(self, **kwargs):
    return self._setFanMode(mode = kwargs['mode'],
                            duty_cycle = kwargs['duty_cycle'],
                            timer = int(kwargs['timer']))


  def cancelFanModeOnWithTimer(self):
    self.postPutDevice({'fan_timer_timeout' : 0})


  def setFanEveryDaySchedule(self, start_hour, end_hour):
    data = {
      'fan_duty_start_time' : start_hour * 3600,
      'fan_duty_end_time' : end_hour * 3600
    }

    self.postPutDevice(json.dumps(data))


  def turnOff(self):
    self.setTargetTemperatureMode('off')


  class action_CurrentWeather(object):
    class Meta(Meta):
      name = 'Weather'
      description = 'Current Weather Details'

    def run(self, outer, *args, **kwargs):
      return outer.currentWeather()


  class action_SetTemperature(object):
    class Meta(Meta):
      name = 'Set temperature'
      description = 'Set temperature on Nest thermostat'

      _outputActionConditions = Conditions()
      _outputActionConditions.add(
        key = 'indoor_temp', type = 'float',
        multiple = False, name = 'Indoor Temperature',
        description = 'Indoor Temperature',
        predicates = ['lt', 'gt'])

      _outputActionConditions.add(
        key = 'indoor_humidity', type = 'float',
        multiple = False, name = 'Outdoor Humidity',
        description = 'Outdoor Humidity',
        predicates = ['eq'])

      _hvac_modes = ConditionValues()
      _hvac_modes.add(key = 'id', value = 1, name = 'Cool',
                     description = 'Air Conditioning Mode')
      _hvac_modes.add(key = 'id', value = 2, name = 'Heat',
                     description = 'Heating Mode')
      _hvac_modes.add(key = 'id', value = 3, name = 'Both',
                     description = 'Both Heat & Cool Mode')

      _outputActionConditions.add(
        key = 'hvac_mode', type = 'dict',
        multiple = False,
        name = 'Heating / Cooling Mode',
        description = 'Heating & Air Conditioning Mode',
        values = _hvac_modes,
        predicates = ['ne', 'gt', 'eq'])

      outputActionConditions = _outputActionConditions.conditions


    def run(self, outer, **kwargs):
      outer.setup()

      temp = outer.tempInput(kwargs['temp'])

      notice('Setting temp to %s' % (temp,))

      data = {
        'target_change_pending' : True,
        'target_temperature' : temp
      }

      outer.postPutShared(json.dumps(data))


  class action_SetFanMode(object):
    class Meta(Meta):
      name = 'Set Fan Status'
      description = 'Turn fan on / auto for Nest thermostat'
      parameters = {'state' : 'Fan state ( on / auto )',
                    'values' : ['on', 'auto']}


    def run(self, outer, *args, **kwargs):
      outer.parent.setup()

      state = kwargs['state']

      if state not in ['on', 'auto'] :
        state = 'auto'

      notice('Setting fan to %s with %s.' % (state, outer.parent.access_token))

      outer.postPutDevice(json.dumps({'fan_mode' : state}))


  class action_ToggleAway(object):
    class Meta(Meta):
      name = 'Toggle Away Status'


    def run(self, outer, **kwargs):
      outer.parent.setup()

      state = kwargs['state'] in outer.truth

      notice('Setting away status to %s with %s'
             % (state, outer.parent.access_token))

      outer.postPutStructure(json.dumps({'away' : state}))


  class action_SetHumidifierStatus(object):
    class Meta(Meta):
      name = 'Enable Humidifier'


    def run(self, outer, **kwargs):
      outer.parent.setup()

      state = kwargs['state'] in outer.truth

      notice('Setting humidifier status to %s with %s'
             % (state, outer.parent.access_token))

      outer.postPutDevice(json.dumps({'target_humidity_enabled' : state}))


  class action_SetHumidity(object):
    class Meta(Meta):
      name = 'Set Humidity'


    def run(self, outer, **kwargs):
      outer.parent.setup()

      humidity = float(kwargs['humidity'])

      notice('Setting humidifier to %s with %s'
             % (humidity, outer.parent.access_token,))

      outer.postPutDevice(json.dumps({'target_humidity' : humidity}))


  class action_SetAutoAwayStatus(object):
    class Meta(Meta):
      name = 'Set Auto Away Status'


    def run(self, outer, **kwargs):
      outer.parent.setup()

      state = kwargs['state'] in outer.truth

      notice('Setting auto away status to %s with %s'
             % (state, outer.parent.access_token, ))

      outer.postPutDevice(json.dumps({'auto_away_enable' : state}))


  class action_SetDualFuelBreakpoint(object):
    class Meta(Meta):
      name = 'Set Dual Fuel Breakpoint'


    def run(self, outer, **kwargs):
      outer.setup()

      breakpoint = kwargs['breakpoint']

      if int(breakpoint) <> 0:
        data = {'dual_fuel_breakpoint_override' : breakpoint}
      else:
        data = {'dual_fuel_breakpoint_override' : 'none',
                'dual_fuel_breakpoint' : breakpoint}

      notice('Setting dual fuel breakpoint to %s with %s'
             % (breakpoint, outer.access_token))

      outer.postPutDevice(json.dumps(data))


  class action_SetAwayStatus(object):
    class Meta(Meta):
      name = 'Set Away'


    def run(self, outer, **kwargs):
      outer.setup()

      state = kwargs['away'] in outer.truth

      notice('Setting auto away status to %s with %s' %
             (state, outer.access_token))

      data = {
        'away' : state,
        'away_timestamp' : time.time(),
        'away_setter' : 0}

      outer.postPutStructure(json.dumps(data))

  def _post(self, post_url, data):
    url = "%s/v2/put/%s" % (self.parent.transport_url, post_url)

    self.request.post(url = url, data = data, headers = self.parent.headers())

  def postPutDevice(self, data):
    self._post('device.%s' % (self.serial,), data)

  def postPutStructure(self, data):
    self._post('structure.%s' % (self.structure_id,), data)

  def postPutShared(self, data):
    return self.request.post('shared.%s' % (self.serial,), data)

