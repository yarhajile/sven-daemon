"""
Copyright (C) 2014, Web Bender Consulting, LLC. - All Rights Reserved
Unauthorized copying of this file, via any medium is strictly prohibited
Proprietary and confidential
Written by Elijah Ethun <elijahe@gmail.com>
"""

"""
Module containing common methods for Sven utility programs.
"""

import os
import time
import inspect
import datetime
import logging
import signal
import traceback
import syslog

logging.basicConfig(level = logging.DEBUG)

# Open the syslog and send a startup message.
syslog.openlog("sven-monitor", syslog.LOG_PID, syslog.LOG_DAEMON)

def callerName(skip=2):
  """Get a name of a caller in the format module.class.method

     `skip` specifies how many levels of stack to skip while getting caller
     name. skip=1 means "who calls me", skip=2 "who calls my caller" etc.

     An empty string is returned if skipped levels exceed stack height

     Source: https://gist.github.com/techtonik/2151727
  """
  stack = inspect.stack()
  start = 0 + skip
  if len(stack) < start + 1:
    return ''
  parentframe = stack[start][0]

  name = []
  module = inspect.getmodule(parentframe)
  # `modname` can be None when frame is executed directly in console
  # TODO(techtonik): consider using __main__
  if module:
      name.append(module.__name__)
  # detect classname
  if 'self' in parentframe.f_locals:
      # I don't know any way to detect call from the object method
      # XXX: there seems to be no way to detect static method call - it will
      #      be just a function call
      name.append(parentframe.f_locals['self'].__class__.__name__)
  codename = parentframe.f_code.co_name
  if codename != '<module>':  # top level usually
      name.append( codename ) # function or a method
  del parentframe
  return ".".join(name)


def notice(message):
  """
  Output a message & write it to the syslog.
  """
  dt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

  if message is list or message is dict :
    syslog.syslog("%s: %s -- %s" % ( callerName(), dt, vars(message) ))
    print( "%s: %s -- %s" % ( callerName(), dt, vars(message) ) )
  else :
    syslog.syslog("%s: %s -- %s" % ( callerName(), dt, str(message) ))
    print( "%s: %s -- %s" % ( callerName(), dt, str(message) ) )



def notify(message):
  """
  This is to notify us when something bad happens internally.
  """
  notice(message)


def debugSignalHandler(sig, frame):
  """
  Signal handler.
  """
  global isRunning

  traceback.print_stack()

  if sig == signal.SIGTERM :
    # Caught a TERM signal. Either a manual shutdown of the service or the 
    # system is shutting down. Toggle the isRunning flag so the daemon will 
    # exit the main polling loop and shutdown gracefully.

    notice("Caught SIGTERM, preparing to stop service.")
    isRunning = False


def listen():
  signal.signal(signal.SIGTERM, debugSignalHandler)
  signal.signal(signal.SIGUSR1, debugSignalHandler)  # Register handler


class Meta(object):
  name = None
  description = None
  outputActionConditions = []
  parameters = {}


class InterfaceMeta(object):
  name = None
  description = None
  parameters = {}


def GetMeta(object):
  output = {}

  output['module_name'] = object.__class__.__name__
  for key in dir(object.Meta):
    if key[0] != '_' :
      output[key] = getattr(object.Meta, key)

  return output


def GetInterfaceMeta(object):
  output = {}

  for key in dir(object.InterfaceMeta):
    if key[0] != '_':
      output[key] = getattr(object.InterfaceMeta, key)

  return output


def changeOwner(user, group, prohibitRoot = True):
  """
  Change current process ownership to desired system UID and GID.
  """

  try:
    if prohibitRoot and (user == 0 or group == 0):
      print "Cannot run as root - Please select another user/group."
      return False

    os.setregid(group, group)
    os.setreuid(user, user)
  except OSError, ex:
    print "Failed to change process ownership: %s" % (ex)
    return False

  return True


def stringToDate(date):
  """
  Convert a ISO date string (YYYY-MM-DD) into a datetime.date object.
  """

  try:
    date = date.split(" ")[0].rstrip().lstrip()
    parts = date.split('-', 2)
    parts = map(lambda p : int(p), parts)

    return datetime.date(parts[0], parts[1], parts[2])
  except :
    raise ValueError, "Invalid date string/format value '%s' passed!" % (date)


def prettyDict(d):
  def pretty(d, indent):
    for i, (key, value) in enumerate(d.iteritems()):
      if isinstance(value, dict):
        print '{0}"{1}": {{'.format('\t' * indent, str(key))
        pretty(value, indent + 1)
        if i == len(d) - 1:
          print '{0}}}'.format('\t' * indent)
        else:
          print '{0}}},'.format('\t' * indent)
      else:
        if i == len(d) - 1:
          print '{0}"{1}": "{2}"'.format('\t' * indent, str(key), value)
        else:
          print '{0}"{1}": "{2}",'.format('\t' * indent, str(key), value)

  print '{'
  pretty(d, indent = 1)
  print '}'