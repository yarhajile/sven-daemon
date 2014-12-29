"""
Copyright (C) 2014, Web Bender Consulting, LLC. - All Rights Reserved
Unauthorized copying of this file, via any medium is strictly prohibited
Proprietary and confidential
Written by Elijah Ethun <elijahe@gmail.com>
"""

import zmq

from Sven.Module.System.Base import Base
from Sven.Methods import *


class SocketServer(Base):
  """
  This simple socket server allows us to have external systems use Sven for
  monitoring.
  """

  required_parameters = ['address', 'port']


  class Meta(Meta):
    """
    Provides details about this module.
    """

    name = 'Socket Server'
    description = 'System Socket Server'


  def threadTarget(self, thread):

    """
    This method is the thread 'target' called from the parent addThread()
    method. The parent addThread() method is typically called from our static
    dispatch method.
    """

    # Setup zmq socket server
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind(self.address)

    getattr(self, self.callback)(socket)

    while thread.running == True:
      address = socket.recv()

      if address is not None:
        for device in self.module_factory.dispatched_modules.SocketServer:
          if address == device.address:
            # Run the callback method set in the admin panel.
            # This will be responsible for processing the input / output from
            # the above RPC server. Address received from the rpc client matches
            # an address we are monitoring, trigger its callback() method.
            device.callback(socket)
      time.sleep(.05)