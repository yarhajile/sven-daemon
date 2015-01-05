"""
Copyright (C) 2014, Web Bender Consulting, LLC. - All Rights Reserved
Unauthorized copying of this file, via any medium is strictly prohibited
Proprietary and confidential
Written by Elijah Ethun <elijahe@gmail.com>
"""

import re
import pyttsx

from Sven.Module.System.Base import Base
from Sven.Methods import *


class Espeak(Base):
  module_parameters = ['espeakvoice', 'espeakrate']
  espeakrate = 165
  espeakvoice = 'en-us'


  def __init__(self, module_factory = None, db = None, id = None):
    super(Espeak, self).__init__(module_factory, db, id)
    self.direction = 'out'


  class Meta(Meta):
    name = 'Text to speech'
    description = 'Espeak text to speech processor'


  def cleanup(self):
    self.engine.endLoop()


  def threadTarget(self, thread):
    self.engine = pyttsx.init()
    self.engine.setProperty('voice', self.espeakvoice)
    self.engine.setProperty('rate', self.espeakrate)
    self.engine.startLoop(False)

    while thread.running == True:
      self.engine.iterate()

      if self.event_triggered is not None:
        self.runTriggeredEvents()

      self.runTimedUpdates(thread)
      time.sleep(.1)


  class action_Speak(object):
    class Meta(Meta):
      name = 'Espeak player'
      parameters = {'text_to_speak': 'Text to speak'}

    def run(self, outer, *args, **kwargs):
      message = kwargs['calling_module'].device_name

      if 'text_to_speak' in kwargs and kwargs['text_to_speak']:
        message = kwargs['text_to_speak']

        # Allow tags such as {{7|methodName|foo:bat,bar:baz}} where 7 is the
        # device_id, methodName is a method in that devices module definition
        # and 'foo' & 'bar' are key => value pairs to pass in to the method.
        tags = re.findall('{{[\s+]*[0-9]*\|[\w+]*[\w+:,|]*}}', message)

        if tags:
          for tag in tags:
            # Clean up the tag first before checking for method and variables,
            # but leave the original intact so we can perform a full string
            # replacement later.
            _tag_stripped = tag.replace('{{', '')
            _tag_stripped = _tag_stripped.replace('}}', '')
            device_id, method, vars = _tag_stripped.split('|')
            _kwargs = {}

            if vars:
              key_values = vars.split(',')
              for key_value in key_values:
                key, value = key_value.split(':')
                _kwargs[key] = value
            device = outer.module_factory.dispatched_modules\
              .getDeviceById(device_id)

            if _kwargs:
              message = message.replace(tag, getattr(device, method)(_kwargs))
            else:
              message = message.replace(tag, getattr(device, method)())

        notice("Espeak playing: %s " % message)
        outer.engine.say(message)
