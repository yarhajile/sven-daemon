"""
Copyright (C) 2014, Web Bender Consulting, LLC. - All Rights Reserved
Unauthorized copying of this file, via any medium is strictly prohibited
Proprietary and confidential
Written by Elijah Ethun <elijahe@gmail.com>
"""
import Sven.Database
import Sven.Module.System.Base

from Sven.Module.System.Base import Base
from Sven.Methods import *


class Dummy(Base):
  class Meta(Meta):
    """
    Provides details about this module.
    """
    name = 'Dummy Module Name - BANE ME'
    description = 'Dummy Module Description'


  def threadTarget(self, thread):
    """
    This method is the thread 'target' called from the parent addThread()
    method. The parent addThread() method is typically called from our static
    dispatch method.
    """

    notice("    Dummy threadTarget initialized")

    while thread.running == True:
      if self.event_triggered is not None:
        self.runTriggeredEvents()

      self.runTimedUpdates(thread)

      time.sleep(.05)


  class action_DummyAction(object):
    class Meta(Meta):
      name = 'Dummy Action Name'
      description = 'Dummy Action Description'

    def run(self, outer, *args, **kwargs):
      """
      Perform a productive output action
      """
