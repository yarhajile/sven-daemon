"""
Copyright (C) 2014, Web Bender Consulting, LLC. - All Rights Reserved
Unauthorized copying of this file, via any medium is strictly prohibited
Proprietary and confidential
Written by Elijah Ethun <elijahe@gmail.com>
"""

from dateutil import parser

import time
import requests
import Sven.Database
import Sven.Requests
import simplejson as json

from Sven.Methods import *
from Sven.Module.Cloud.Base import Base

class Nest(Base):
  """
  Control the Nest learning thermostat... or dutifully attempt to.
  """

  LOGIN_URL = 'https://home.nest.com/user/login'

  module_parameters = ['username', 'password']
  required_parameters = ['username', 'password']

  class Meta(Meta):
    name = 'Nest Account'

  def __init__(self, module_factory = None, db = None, id = None):
    super(Nest, self).__init__(module_factory, db, id)

    self.direction = 'both'
    self.status = None
    self.userid = None
    self.access_token = None
    self.token_expires = None
    self.transport_url = None
    self.request = Sven.Requests.Requests()


  def threadTarget(self, thread):
    """
    This method is the thread 'target' called from the parent addThread() 
    method. The parent addThread() method is typically called from our static 
    dispatch method.
    """

    while thread.running == True :
      if self.event_triggered is not None :
        self.runTriggeredEvents()

      self.runTimedUpdates(thread)

      # Aint much to do in this thread since the children handle connecting to 
      # the Nest system via self.parent.setup( force_reload_status = True ).
      time.sleep(.5)


  @classmethod
  def dispatch(cls, module_factory, db, _temp, **kwargs):
    """
    Override the moduleBase.dispatch() method because we want NestThermostat 
    and NestProtect modules to be loaded AFTER this is all setup.
    """

    if 'device_id' in kwargs:
      try :
        object = Nest(module_factory = module_factory, db = db,
                      id = kwargs['device_id'])

        # Hand it off to the thread handler
        object.addThread()
      except:
        notice(traceback.format_exc())

      return

    cursor = db.execute("SELECT device_id FROM devices_%s "
                        "WHERE location_group_active = true "
                        "AND location_active = true "
                        "AND device_active = true" % 
                        cls.__name__)
    
    values = cursor.fetchall()
    parent_started = False

    for value in values:
      try:
        object = Nest(module_factory = module_factory, db = db,
                      id = value['device_id'])

        # Hand it off to the thread handler
        object.addThread()
        parent_started = True
      except:
        notice(traceback.format_exc())

    if parent_started is True:
      # Now that the parent nest account modules are live, attach the children 
      # NestThermostat and NestProtect modules.
      try :
        from Sven.Module.Cloud.NestThermostat import NestThermostat
        from Sven.Module.Cloud.NestProtect import NestProtect
        NestThermostat.dispatch(module_factory, db)
        NestProtect.dispatch(module_factory, db)
      except :
        notice(traceback.format_exc())


  def headers(self, extra_headers = None):
    headers = {
      'user-agent' : str('Nest/1.1.0.10 CFNetwork/548.0.4'),
      'X-nl-protocol-version' : int(1)
    }

    if self.userid is not None:
      headers.update({
        'X-nl-user-id' : int(self.userid),
        'Authorization' : str('Basic ' + self.access_token)
      })

    if extra_headers is not None:
      headers.update(extra_headers)

    return headers


  def setup(self, force_reload_status = None):
    self.login()

    if force_reload_status is not None:
      self.getStatus()


  def login(self):
    try:
      # Thu, 16-Oct-2014 17:48:45 GMT
      if self.token_expires is not None:
        datetime = parser.parse(self.token_expires)

        expires_timestamp = int(time.mktime(datetime.timetuple()))

        if time.time() < expires_timestamp:
          notice('Nest authentication token still valid.')
          return

      response = self.request.post(self.LOGIN_URL,
                                   data = {'username' : self.username,
                                           'password' : self.password},
                                   headers = self.headers()).json()
      notice(response)

      self.userid = response['userid']
      self.access_token = response['access_token']
      self.token_expires = response['expires_in']
      self.transport_url = response['urls']['transport_url']
      self.weather_url = response['urls']['weather_url']
      self.email = response['email']
      self.limits = response['limits']
      self.weave = response['weave']
    except:
      notice(traceback.format_exc())


  def getStatus(self):
    self.status = self.request.get(
      self.transport_url + '/v2/mobile/user.' + self.userid,
      headers = self.headers()).json()
    notice("Updated Nest status!")


  def getWeather(self, postal_code):
    return self.request.get(
      "https://home.nest.com/api/0.1/weather/forecast/%s" % postal_code).json()


  def getUserLocations(self):
    self.setup()
    user_structures = []
    status = self.status

    for structure_id, structure_details in self.status['structure'].iteritems():

      protects = []
      thermostats = []

      for protect in getattr(status, 'topaz', []):
        if protect['structure_id'] == structure_id :
          protects.append(protect)
          # @todo Add the "where" name when we know where to get it from.

      # Build links for Thermostat devices from 'links'.
      # @todo I don't have a 'Protect' device, so those *may* be linked in
      # here as well,which would need to be filtered or discovered differently.
      for device_id, device_details in status['link'].iteritems():
        if device_details['structure'] == 'structure.%s' % structure_id:
          data = status['device'][device_id]

          # Set the 'where' location of the device.
          for where in status['where'][structure_id]['wheres']:
            if where['where_id'] == status['device'][device_id]['where_id']:
              data['where'] = where['name']

          thermostats.append({device_id : data})

      user_structures.append({structure_id : {
        'name' : structure_details['name'],
        'address' : getattr(structure_details, 'street_address', None),
        'city' : getattr(structure_details, 'location', None),
        'postal_code' : structure_details['postal_code'],
        'country' : structure_details['country_code'],
        'weather_data' : self.getWeather(structure_details['postal_code']),
        'away' : structure_details['away'],
        'away_last_changed' : structure_details['away_timestamp'],
        'thermostats' : thermostats,
        'protects' : protects
      }})

    return user_structures


  def getWhere(self, where_id):
    for where in self.status['where'][self.structure_id]['wheres']:
      if where_id == where['where_id']:
        return where['name']
    return where_id


  def getDeviceNetworkInfo(self):
    connection_info = self.status['track'][self.serial]
    device = self.status['device'][self.serial]

    return {
      'online' : connection_info['online'],
      'last_connection' : connection_info['last_connection'],
      'wan_ip' : getattr(connection_info, 'last_ip', None),
      'local_ip' : device['local_ip'],
      'mac_address' : device['mac_address']
    }

  #
  # Output Actions
  #
  class action_getDeviceNetworkInfo(object):
    class Meta(Meta):
      name = 'Get available device network info'
      outputActionIgnore = True

    def run(self, outer):
      outer.setup()
      return outer.getDeviceNetworkInfo()

  class action_GetDeviceList(object):
    class Meta(Meta):
      name = 'Device Listing'
      description = 'Shows available nest devices for this account'
      outputActionIgnore = True

    def run(self, outer, **kwargs):
      outer.setup()
      return outer.getUserLocations()

