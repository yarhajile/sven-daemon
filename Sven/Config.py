"""
Copyright (C) 2014, Web Bender Consulting, LLC. - All Rights Reserved
Unauthorized copying of this file, via any medium is strictly prohibited
Proprietary and confidential
Written by Elijah Ethun <elijahe@gmail.com>
"""

"""
Module containing a generic class for parsing a common configuration file format of Sven utility programs.
"""

class Config(object):
  """
  Class handling the reading and parsing of runtime configuration values
  from file.
  """

  def __init__(self):
    """
    Constructor.
    """
    self.file_name   = ""
    self.options    = {}


  def setFileName(self, file_name):
    """
    Set the file name.
    """
    self.file_name = file_name


  def getFileName(self):
    """
    Get the file name.
    """
    return self.file_name


  def parse(self):
    """
    Read all configuration options from file.
    """
    handle = file(self.file_name, "r")
    lines = handle.readlines()
    handle.close()

    # Since we're building a dict of key/value pairs from the configuration
    # file, drop all the newlines, leading and trailing whitespace. We ignore
    # lines that begin with #.

    lines = map(lambda l: l.rstrip('\n'), lines)
    lines = map(lambda l: l.strip(), lines)
    lines = filter(lambda l: l != "" and l[0] != "#", lines)

    #
    # Now split each line into key/value pairs, stripping the leading and
    # trailing whitespace from each pair. Then place the pair in the options
    # dict.
    #

    for line in lines:
      key, value = line.split("=", 1)

      if not key:
        continue

      if not value:
        value = None
      else:
        value = value.strip()

      self.options[key.strip().lower()] = value


  def validate(self):
    """
    Sanity check all configuration options.
    """
    raise RuntimeError("Function must be defined by derived class!")


  def __len__(self):
    """
    Handle dictionary length requests.
    """
    return len(self.options)


  def __getitem__(self, key):
    """
    Handle dictionary get requests.
    """
    return self.options[key]


  def __setitem__(self, key, value):
    """
    Handle dictionary set requests.
    """
    self.options[key] = value


  def __delitem__(self, key):
    """
    Handle dictionary delete requests.
    """
    del self.options[key]

