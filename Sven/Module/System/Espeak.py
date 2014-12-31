"""
Copyright (C) 2014, Web Bender Consulting, LLC. - All Rights Reserved
Unauthorized copying of this file, via any medium is strictly prohibited
Proprietary and confidential
Written by Elijah Ethun <elijahe@gmail.com>
"""

import pyttsx

from Sven.Module.System.Base import Base
from Sven.Methods import *


class Espeak(Base):
  module_parameters = ['espeakvoice', 'espeakrate']
  espeakrate = 175
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
        notice("Espeak playing: %s " % message)
        outer.engine.say(message)
