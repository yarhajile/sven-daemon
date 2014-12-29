"""
Copyright (C) 2014, Web Bender Consulting, LLC. - All Rights Reserved
Unauthorized copying of this file, via any medium is strictly prohibited
Proprietary and confidential
Written by Elijah Ethun <elijahe@gmail.com>
"""

import threading

from Sven.Methods import *


class Thread(threading.Thread):
  """
  Threading handler to interface with passed in source objects threadTarget()
  method.
  """

  def __init__(self, source_object):
    threading.Thread.__init__(self)

    self.name = source_object.__class__.__name__
    self.source_object = source_object
    self.running = True


  # This is ran when ModuleBase.addThread() executes our .start( ) method.
  def run(self):
    """
    Calls the source_object's threadTarget() method
    """
    try :
      notice("\n\t%s" % ('-' * 80,))
      notice("\tthreadTarget() firing for %s" % self.name)
      notice("\t%s\n" % ('-' * 80,))

      #pass in thread so we can monitor the run state
      self.source_object.threadTarget(self)
    except AttributeError as ex :
      notice(ex.args[0])


  def stop(self):
    """
    threadTarget()'s will be "while self.running == True:", so stop them from
    the outside when commanded.
    """
    self.running = False
    self.source_object.cleanup()
