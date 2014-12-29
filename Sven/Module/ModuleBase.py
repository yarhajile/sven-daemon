"""
Copyright (C) 2014, Web Bender Consulting, LLC. - All Rights Reserved
Unauthorized copying of this file, via any medium is strictly prohibited
Proprietary and confidential
Written by Elijah Ethun <elijahe@gmail.com>
"""

import os
import re
import json
import time
import string
import pkgutil
import traceback
import simplejson as json

from datetime import *
from Sven.Thread import Thread
from Sven.Database import Database
from Sven.Methods import *

import Sven.Thread
import Sven.Database


class ModuleBase(object):
  """
  Abstract class methods for Sven
  """

  event_triggered = None
  device_parameters = None
  required_parameters = []
  module_parameters = []
  callback_action_cache = []
  output_action_conditions = None
  common_parameters = ['interface', 'bus']

  # Set this to true in an extended module in order to force the dispatcher
  # to ignore that module.
  module_factory_ignore = False

  # Set this to true in an extended module in order to force the dispatcher
  # to ignore that module in the output action list.
  output_action_ignore = False

  address = None
  direction = None
  web_socket = None
  device_name = None
  device_description = None
  location_id = None
  location_name = None
  location_group_id = None
  location_group_name = None

  truth   = [True, 'true', '1', 't', 'y', 'yes']
  untruth = [False, 'false', '0', 'f', 'n', 'no']

  def __init__(self, module_factory, db, id):
    """
    Constructor

    @param module_factory:
    @param db:
    @param id:
    @return:
    """

    self.db = db
    self.id = id
    self.device_type = self.__module__
    self.module_factory = module_factory
    self.last_execution_time = time.time()
    self.object_name = self.__module__
    self.build(db)
    self.setOutputActionConditions()


  def __del__(self):
    self.cleanup()


  def build(self, db):
    sql = "SELECT parameter, value FROM monitor_device_parameter " \
          "WHERE device_id = %s"
    cursor = db.execute(sql , (self.id,))
    self.device_parameters = cursor.fetchall()

    if self.device_parameters:
        self.parameterCheck()
    else:
        raise Exception("No device parameters found for device id %s" %
                         (self.id))

    # Populate device details such as name and description
    cursor = db.execute("SELECT * FROM devices_all WHERE device_id = %s",
                        (self.id,))

    deviceDetails = cursor.fetchone()

    self.device_name = deviceDetails['device_name']
    self.device_description = deviceDetails['device_description']
    self.location_id = deviceDetails['location_id']
    self.location_name = deviceDetails['location_name']
    self.location_group_id = deviceDetails['location_group_id']
    self.location_group_name = deviceDetails['location_group_name']


  def moduleDetails(self):
    notice({
        'id' : self.id,
        'module' : self.object_name,
        'device_name' : self.device_name,
        'location_id' : self.location_id,
        'location_name' : self.location_name,
        'location_group_id' : self.location_group_id,
        'location_group_name' : self.location_group_name
    })


  def parameterCheck(self):
    """
    Some common parameters we want to evaluate & set
    """

    for parameter in self.device_parameters:
      name = parameter['parameter']
      value = parameter['value']

      # Address check
      if name == 'address':
        try:
          value = int(value)
        except ValueError:
          pass

        setattr(self, 'address', value)
      else:
        setattr(self, name, value)


    for parameter in self.required_parameters:
      if not getattr(self, parameter):
        raise Exception('Required parameter %s not set!' % parameter)


  def addThread(self):
    """
    Add new thread
    """

    thread = Sven.Thread.Thread(self)
    thread.start()

    # Append to the module_factory's module list
    self.module_factory.addModule(self)

    # Append to the module_factory's thread list
    self.module_factory.addThread(thread)

    notice_string = \
      '\tA new thread has been added with the following parameters:\n' \
      '\t\tid : %s\n' \
      '\t\tmodule : %s\n' \
      '\t\tdevice_name : %s\n' \
      '\t\tlocation_id : %s\n' \
      '\t\tlocation_name : %s\n' \
      '\t\tlocation_group_id : %s\n' \
      '\t\tlocation_group_name : %s\n' \
      % (str(self.id), str(self.object_name), str(self.device_name),
         str(self.location_id), str(self.location_name),
         str(self.location_group_id), str(self.location_group_name))

    for parameter in self.device_parameters:
      name = parameter['parameter']
      value = parameter['value']

      notice_string += '\t\t%s : %s\n' % (str(name), str(value))

    for module_parameter in self.module_parameters:
      notice_string += "%s : %s\n" % \
                      (module_parameter, getattr(self, module_parameter))

    notice(notice_string)


  def runTimedUpdates(self, thread):
    """
    Poll for updates that the module is looking for
    """

    current_execution_time = time.time()

    if current_execution_time >= self.last_execution_time + \
        int(self.module_factory.config['update_timer_interval']):
      self.handleUpdates(thread)
      # Maybe the updates take a long time to run? Use the current time for
      # the lastExecution time instead of currentExecutionTime
      self.last_execution_time = time.time()


  @classmethod
  def dispatch(cls, module_factory, db, _temp, **kwargs):
    """
    General purpose module dispatcher
    """

    if 'device_id' in kwargs:
      try:
        object = getattr(_temp, cls.__name__)(module_factory = module_factory,
                                              db = db, id = kwargs['device_id'])

        # Hand it off to the thread handler
        object.addThread()
      except:
        notice(traceback.format_exc())
      return

    cursor = db.execute("SELECT device_id FROM devices_%s "
                        "WHERE location_group_active = true "
                        "AND location_active = true "
                        "AND device_active = true" % cls.__name__)

    values = cursor.fetchall()

    for value in values:
      try:
        object = getattr(_temp, cls.__name__)(module_factory = module_factory,
                                              db = db, id = value['device_id'])

        # Hand it off to the thread handler
        object.addThread()
      except:
        notice(traceback.format_exc())


  def cleanup(self):
    """
    Called on thread shutdown
    """

    pass


  def setOutputActionConditions(self):
    """
    Conditions we would like the front-end to consider for execution of output
    action_*() methods
    """

    pass


  def eventDetected(self, details = None):
    """
    @param details:
    @return:
    """

    jsonMessage = {
      'module': self.__module__,
      'details' : details,
      'id':self.id
    }

    # Append all 'moduleParameters' to the message
    for module_parameter in self.module_parameters:
      jsonMessage.update({ module_parameter : getattr(self, module_parameter) })

    self.module_factory.queueInsertEvent(created = datetime.datetime.now(),
                                        updated = datetime.datetime.now(),
                                        message = str(json.dumps(jsonMessage)))


  def removeEvent(self):
    """
    This serves as a post-hook method after handleUpdates() has determined
    that updates should be performed on a device.
    """

    pass


  def handleUpdates(self, thread, db = None):
    """
    Called every few seconds from the daemon monitor to perform updates to
    this thread.

    Each individual module thread executes this method in order to perform
    updates on itself. They MUST provide a database instance to operate on
    within themselves.  This allows them to perform actions on that database
    instance individually as well as providing this parent method a means to
    scan for changes in a global manner independent of the underlying
    inherited modules.
    """

    close_db = False

    if db == None:
      db = Sven.Database.Database.open(self.module_factory.config)
      close_db = True

    if hasattr(self, 'devices'):
      for device in self.devices:
        device.handleUpdates(thread)
      return

    cursor = db.execute("SELECT id, active FROM monitor_device "
                        "WHERE id = %s and update_trigger = true", (self.id,))

    update = cursor.fetchone()

    if update:
      if update['active'] == 0:
        # Thread suicide coming up since we've deactivated the device in the
        # front-end
        notice("Deactivating device id %s" % self.id)

        thread.running = False

        # Return false so that children don't try to reload the thread
        return False


      # @todo Not all scenarios will require a complete rebuild of the thread.
      # Updating the values will be sufficient in most cases

      notice("Tearing down the current %s thread for device id '%s' and "
             "rebuilding it with new values..." %
             (self.__class__.__name__, self.id))

      # Remove any event detection
      self.removeEvent()

      db.execute("UPDATE monitor_device SET update_trigger = false "
                 "WHERE id = %s", (self.id,))
      db.commit()

      try:
        # Rebuild the object with updated parameters
        self.build(db)
      except:
        # Something went wonky rebuilding the object or adding the event, go
        # tell mom & dad.
        notify(traceback.format_exc())

      if close_db:
        db.close()


  def queueEventTriggers(self, *args, **kwargs):
    """
    Maintain thread concurrency by adding execution triggers for the
    threadTargets while loop to execute when an action occurs.

    This is typically executed through the devices callback() method when
    something occurs.  We then add to this list the action_METHOD() we want
    to call.  If an item is added to this dict, the next loop of the
    threadTarget() while loop will run the 'actionsToPerform' in itself.

    @param actions:
    @return:
    """
    notice(kwargs['actions'])

    self.event_triggered = {'calling_module' : kwargs['calling_module'],
                           'actions_to_perform' : kwargs['actions']}


  def runTriggeredEvents(self):
    """
    Called from the thread target loop to perform the individual actions.

    self.eventTriggered is a dict of {'calling_module' : <object>,
    'actions_to_perform' : [{'action' : 'chirp' : {'parameters' :
    {'parameter1, 'parameter2' }}]}

    @return:
    """

    for action_to_perform in self.event_triggered['actions_to_perform']:
      self.runTriggeredEvent(calling_module = self.event_triggered['calling_module'],
                             action = action_to_perform['action'],
                             parameters = action_to_perform['parameters'])

    # Reset the eventTriggered dict
    self.event_triggered = None


  def runTriggeredEvent(self, **kwargs):
    """
    This is abstracted out from the runTriggeredEvents() above so that we can
    call actions individually and immediately without running them through
    the triggered events queue, like from the websockets.

    @param kwargs:
    @return:
    """

    # Allow us to call actions without the action_ prefix
    if not re.match('^action_', kwargs['action']):
      kwargs['action'] = 'action_' + kwargs['action']

    notice("runTriggeredEvent() with %s" % kwargs['action'])


    try:
      object = getattr(self, kwargs['action'])()
      return object.run(self, calling_module = kwargs['calling_module'],
                        **kwargs['parameters'])
    except:
      notice(traceback.format_exc())


  def threadTarget(self, thread):
    """
    Force subclasses to define a threadTarget method.
    """

    raise NotImplementedError


  def getDeviceById(self, device_id):
    return self.module_factory.dispatched_modules.getDeviceById(device_id)


  def getCallbackActionsPREVIOUS(self):
    output = [];

    if not self.callback_action_cache:
      notice("Fetched new callback actions from db for device id %s" %
             str(self.id))
      db = Sven.Database.Database.open(self.module_factory.config)
      cursor = db.execute("SELECT output_device_id, action, parameters, "
                          "arm_status_id, arm_status_device, "
                          "arm_status_location, arm_status_location_group "
                          "FROM device_output_actions WHERE id = %s",
                          (self.id,))

      self.callback_action_cache = cursor.fetchall()

    actions = self.callback_action_cache
    notice(actions)

    for action in actions:
      found = False

      # Don't fire this action if there is an alarm status override for the
      # device that doesn't match the parent status.
      if action['arm_status_device'] > 0 and \
              action['arm_status_device'] != action['arm_status_id']:
        continue

      # Don't fire the action if there is an alarm status override for the
      # location that doesn't match the parent status.
      if (
        action['arm_status_location'] > 0
        and action['arm_status_location'] != action['arm_status_id']
        and action['arm_status_device'] != action['arm_status_id']
     ):
        continue

      # Don't fire the action if the group status doesn't match
      if (
        action['arm_status_location_group'] > 0
        and action['arm_status_location_group'] != action['arm_status_id']
        and action['arm_status_location'] != action['arm_status_id']
        and action['arm_status_device'] != action['arm_status_id']
     ):
        continue

      # Arm status filtering passed, both device and location armed status
      # must be 0 and the group status matches our current armed state.
      for element in output:
        if element['output_device_id'] == action['output_device_id']:
          found = True
          element['output_actions'].append(
            {'action' : action['action'],
             'parameters' : json.loads(action['parameters'])})

      if found == False:
        output.append(
          {'output_device_id' : action['output_device_id'],
           'output_actions' : [
             {'action' : action['action'],
              'parameters' : json.loads(action['parameters'])}]})

    return output


  def getCallbackActions(self):
    output = [];

    if not self.callback_action_cache:
      notice("Fetched new callback actions from db for device id %s" %
             (str(self.id),))
      db = Sven.Database.Database.open(self.module_factory.config)
      cursor = db.execute("SELECT output_device_id, action, parameters "
                          "FROM device_output_actions "
                          "WHERE id = %s",
                          (self.id,))

      self.callback_action_cache = cursor.fetchall()

    actions = self.callback_action_cache

    notice(actions)

    for action in actions:
      found = False
      parameters = {}

      # Rebuild the parameters as a dict as
      # {'custom_key_name' : 'custom_key_value'} vs
      # {'key' : 'custom_key_name', 'value' : 'custom_key_value'}
      for parameter in json.loads(action['parameters']):
        parameters[parameter['key']] = parameter['value']

      # Arm status filtering passed, both device and location armed status must
      # be 0 and the group status matches our current armed state
      for element in output:
        if element['output_device_id'] == action['output_device_id']:
          found = True
          element['output_actions'].append({'action' : action['action'],
                                            'parameters' : parameters})

      if found == False:
        output.append({
          'output_device_id' : action['output_device_id'],
          'output_actions' : [
            {
              'action' : action['action'],
             'parameters' : parameters
            }]})

    return output


  def callback(self, *args, **kwargs):
    """
    This is executed when any input event occurs.
    """

    message = \
      '\tDevice activated at %s with the following parameters:\n' \
      '\t\tid : %s\n' \
      '\t\tmodule : %s\n' \
      '\t\tdevice_name : %s\n' \
      '\t\tlocation_id : %s\n' \
      '\t\tlocation_name : %s\n' \
      '\t\tlocation_group_id : %s\n' \
      '\t\tlocation_group_name : %s\n' \
      % (time.strftime("%a, %d %b %Y %H:%M:%S"), str(self.id),
         str(self.object_name), str(self.device_name), str(self.location_id),
         str(self.location_name), str(self.location_group_id),
         str(self.location_group_name))

    for module_parameter in self.module_parameters:
      message += "%s : %s\n" % (module_parameter, getattr(self, module_parameter))

    self.eventDetected(message)

    notice(message)

    # List of ALL actions we will be performing each time the callback is
    # called for this specific device.
    for action_device in self.getCallbackActions():
      # All output devices we have on file, used to match up the id's from
      # the front-end with the actual running threads.
      for device in self.module_factory.dispatched_modules.getAllOutputDevices():
        if int(device.id) == int(action_device['output_device_id']):
          # We matched up our front-end action to a running thread.
          #  Make sure that all conditions match.
          # 'actions' is a dict of 'action' and its accompanying 'parameters'
          device.queueEventTriggers(actions = action_device['output_actions'],
                                    calling_module = self)

          # This may not be necessary, but allows us to trigger additional
          # actions tied to the output device
#          device.callback()
    return message


  def loadJson(self, resource):
    if hasattr(json, "loads"):
      return json.loads(resource)
    else:
      return json.read(resource)


  def getWebSocketServer(self):
    if self.web_socket is None:
      for device in self.module_factory.dispatched_modules.getAllDevices():
        # @todo This needs more attention, what if we have more than one
        # websocketserver established?
        if device.__class__.__name__ == 'WebSocketServer':
          self.web_socket = device.server
          break

    return self.web_socket


  class action_DispatchModule(object):
    class Meta(Meta):
      name = 'Dispatch Module'
      description = 'Dispatches a new module if it not already in the factory'
      output_action_ignore = True

    def run(self, outer, *args, **kwargs):
      # This is tricky, for most modules, we can simply pass in the id to the
      # modules dispatch method and have them perform an additional check that
      # 'if id is not None, then dispatch by id instead of finding the list of
      # id's for the module in the db.
      #
      # However, this doesn't work for modules that have sub modules, like
      # RCSwitch.  In that case, we also need to know the address we'll be
      # appending the child object to.
      try:
        _name = 'Sven.Module.%s.%s' % (kwargs['input_interface'], kwargs['input_bus'])
        _temp = __import__(_name, globals(), locals(), [kwargs['input_bus']])
        module = getattr(_temp, kwargs['input_bus'])

        # Skip execution if the module is already active
        if outer.module_factory.dispatched_modules.getDeviceById(
            int(kwargs['device_id'])):
          notice("Device id %s already dispatched" % kwargs['device_id'])
          return

        # Execute the classes dispatch() method, passing in the factory module,
        # its database instance and parameters passed in.
        notice("**************************************")
        notice("Dispatching new module")
        module.dispatch(outer.module_factory, outer.module_factory.db, _temp,
                        **kwargs)
        notice("***************************************")
      except:
        return traceback.format_exc()


  class action_ModuleListing(object):
    class Meta(Meta):
      name = 'Module listing'
      description = 'Lists all available modules'
      output_action_ignore = True

    def run(self, outer, *args, **kwargs):
      output = {}

      for interface in list(outer.module_factory.config['interfaces'].split(',')):
        try:
          base = __import__('Sven.Module.' + interface + '.Base')
          pkgpath = os.path.dirname(base.__file__) + '/Module/' + interface
          modules = [name for _, name, _ in pkgutil.iter_modules([pkgpath])]

          if not hasattr(output, interface):
            output[interface] = { 'modules' : [] }

          for module_name in modules:
            try:
              _name = 'Sven.Module.%s.%s' % (interface, module_name)
              _temp = __import__(_name, globals(), locals(), [module_name])

              module = getattr(_temp, module_name)

              # Skip execution if the module tells us so
              if module.output_action_ignore == True \
                  or module_name == 'Base' \
                  or not getattr(module, 'dispatch'):
                continue

              if not hasattr(output[interface], 'interface_meta'):
                output[interface]['interface_meta'] = GetInterfaceMeta(module)

              output[interface]['modules'].append({
                'module' : module_name,
                'parameters_available' : module.module_parameters,
                'parameters_required' : module.required_parameters,
                'meta' : GetMeta(module)
              })
            except:
              notice(traceback.format_exc())
        except:
          notice(traceback.format_exc())

      return output


  class action_ModuleFactoryStatus(object):
    class Meta(Meta):
      name = 'Module Factory Status'
      output_action_ignore = True


    def run(self, outer, *args, **kwargs):
      output = {}

      all_output_devices = outer.module_factory.dispatched_modules.getAllDevices()

      for device in all_output_devices:
        device_type = device.device_type

        if device.address:
          device_type += '_%s' % str(device.address)

        if not hasattr(output, device_type):
          output[device_type] = {
            'meta' : GetMeta(device),
            'parameters' : device.device_parameters,
            'device_id' : device.id,
            'device_name' : device.device_name,
            'location_id' : device.location_id,
            'location_name' : device.location_name,
            'location_group_id' : device.location_group_id,
            'location_group_name' : device.location_group_name,
          }

          if hasattr(device, 'devices'):
            component_devices = []

            for component_device in device.devices:
              component_devices.append({
                'meta' : GetMeta(component_device),
                'parameters' : component_device.device_parameters,
                'device_id' : component_device.id,
                'device_name' : component_device.device_name,
                'location_id' : component_device.location_id,
                'location_name' : component_device.location_name,
                'location_group_id' : component_device.location_group_id,
                'location_group_name' : component_device.location_group_name,
              })

            output[device_type]['devices'] = component_devices

      return output


  class action_ResetOutputActionCacheForDevice(object):
    class Meta(Meta):
      name = 'Output Action Cache Reset'
      output_action_ignore = True


    def run(self, outer, *args, **kwargs):
      outer.callback_action_cache = []


  class action_FetchConditions(object):
    class Meta(Meta):
      name = 'Fetch Conditions'
      output_action_ignore = True


    def run(self, outer, *args, **kwargs):
      try:
        return outer.conditions().toJSON()
      except:
        notice(traceback.format_exc())


  class action_OutputActions(object):
    class Meta(Meta):
      name        = 'Output Actions'
      description = 'Shows all output actions'
      output_action_ignore = True


    def run(self, outer, *args, **kwargs):
      output = {}

      all_output_devices = outer.module_factory.dispatched_modules\
        .getAllOutputDevices()

      for device in all_output_devices:
        device_type = device.device_type

        if hasattr(device, 'address') and device.address is not None:
            device_type += '_%s' % str(device.address)

        if not hasattr(output, device_type):
          conditions = []

          if device.output_action_conditions is not None:
            try:
              conditions = device.output_action_conditions.conditions
            except:
              notice(traceback.format_exc())

          output[device_type] = {
            'meta' : GetMeta(device),
            'actions' : [],
            'parameters' : device.device_parameters,
            'conditions' : conditions,
            'device_id' : device.id,
            'device_name' : device.device_name,
            'location_id' : device.location_id,
            'location_name' : device.location_name,
            'location_group_id' : device.location_group_id,
            'location_group_name' : device.location_group_name,
          }

      for device in all_output_devices:
        device_type = device.device_type

        if hasattr(device, 'address') and device.address is not None:
          device_type += '_%s' % str(device.address)

        for attribute in dir(device):
          if re.match('^action_', attribute):
            # This comment is self explanatory
            meta = GetMeta(getattr(device, attribute))

            # If the action_* class meta data has a 'output_action_ignore' field,
            # ignore it since this is an action we don't want callable by input
            # events.
            if not 'output_action_ignore' in meta:
              output[device_type]['actions'].append({
                'meta' : meta,
                'action' : attribute,
                'parameters' : device.device_parameters,
                'device_id' : device.id,
              })

      return output