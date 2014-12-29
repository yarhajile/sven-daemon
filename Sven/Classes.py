"""
Copyright (C) 2014, Web Bender Consulting, LLC. - All Rights Reserved
Unauthorized copying of this file, via any medium is strictly prohibited
Proprietary and confidential
Written by Elijah Ethun <elijahe@gmail.com>
"""

import sys

import Sven.Methods
import Sven.Config
import Sven.Exception

class Config(Sven.Config.Config) :
  """
  Class handling the reading and parsing of runtime configuration values from
  file.
  """

  def __init__(self):
    super(Config, self).__init__()

    # Perform additional validation rules here against config file
    try :
      pass

    except IndexError:
      sys.exit(-1)


  def validate(self):
    """
    Sanity check all configuration options.
    """
    pass
