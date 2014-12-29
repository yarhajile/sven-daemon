"""
Copyright (C) 2014, Web Bender Consulting, LLC. - All Rights Reserved
Unauthorized copying of this file, via any medium is strictly prohibited
Proprietary and confidential
Written by Elijah Ethun <elijahe@gmail.com>
"""

"""
Holds instances of threads.
"""

import time
import os.path
import traceback
import pkgutil

from Sven.Methods import *

class ThreadContainer(object):
  def __init__(self):
      self.threads = []

  def add(self, object):
      self.threads.append(object)