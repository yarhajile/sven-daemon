"""
Copyright (C) 2014, Web Bender Consulting, LLC. - All Rights Reserved
Unauthorized copying of this file, via any medium is strictly prohibited
Proprietary and confidential
Written by Elijah Ethun <elijahe@gmail.com>
"""

import json

from Sven.Module.System.Base import Base
from Sven.SimpleWebSocketServer import *
from Sven.Methods import *


class WebSocketServer(Base):
  module_parameters = ['address', 'port']
  required_parameters = ['address', 'port']

  def __init__(self, module_factory = None, db = None, id = None):
    super(WebSocketServer, self).__init__(module_factory, db, id)
    self.port = int(self.port)


  class Meta(Meta):
    name = 'WebSocket Server'


  def cleanup(self):
    self.server.shutdown()


  def threadTarget(self, thread):
    class SimpleEcho(WebSocket):
      def handleMessage(self):
        if self.data is None:
          self.data = ''

        notice("Handling WebSocket message: %s" % str(self.data))

        output = self.server.callingObject.callback(message = str(self.data))
        self.sendMessage(str(json.dumps(output)))


      def handleConnected(self):
        print self.address, 'connected'


      def handleClose(self):
        print self.address, 'closed'


    class SvenWebSocketServer(SimpleWebSocketServer):
      def broadcastMessage(self, data, callback, message):
        for client in self.connections.itervalues():
          if client != self:
            try:
              client.sendMessage(str(json.dumps(
                {'data': data, 'callback': callback, 'message': message})))
            except:
              notice(traceback.format_exc())

    self.server = SvenWebSocketServer(self.address, self.port, SimpleEcho)
    # Make this instance available to the socket server so that we can make
    # db calls.
    self.server.callingObject = self
    self.server.serveforever()


  def callback(self, *args, **kwargs):
    """
    Called from WebSocketsHandler.on_message() via threadTarget starting up the
    server.
    """

    # Perform global actions when a monitored event occurs
    super(WebSocketServer, self).callback(args, kwargs)

    output = {
      'callback': None,
      'data': {},
      'message': ''
    }

    try:
      message = json.loads(kwargs['message'])

      action = message.get('action', None)
      # If no device_id is passed, assume we're using our own methods
      device_id = int(message.get('device_id', self.id))
      callback = message.get('callback', None)
      parameters = message.get('parameters', {})

      output['callback'] = callback

      if action and device_id:
        # No sense in looping over every device if we are working on ourself.
        if device_id == self.id:
          device = self
        else:
          notice("Fetching device by id.")
          device = self.module_factory.dispatched_modules\
            .getDeviceById(device_id)

        if device is None:
          output['message'] = 'Unable to run %s for device id %s.  Device ' \
                              'might not be active in daemon.' \
                              % (action, device_id, )
          return output

        output['message'] = 'Running %s on %s.' % (action, device.object_name)

        if action == 'callback':
          # Run all actions associated with the device_id
          output['data'] = device.callback()
        else:
          # Run a single action on the module
          notice('*************')
          notice(action)
          notice(parameters)
          try:
            output['data'] = device.runTriggeredEvent(calling_module = self,
                                                      action = action,
                                                      parameters = parameters)
            notice("Executed triggered event")
          except:
            output['data'] = {}
            notice("Execution of triggered event failed!")
            notice(" NOTE: Make sure that action_* run() method has **kwargs "
                   "set!!!")
            notice(traceback.format_exc())
          notice('*************')
        notice(output['message'])

        notice('New WebSocket message')
        notice('    Input:')
        notice(message)
        notice('    Command: %s.%s()' % (device.object_name, action))
        notice('    Output:')
        notice(output)
        notice('--------------')

        return output

    except Exception as ex:
      notice(traceback.format_exc())
      output['message'] = ex
      return output
