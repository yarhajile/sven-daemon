"""
Copyright (C) 2014, Web Bender Consulting, LLC. - All Rights Reserved
Unauthorized copying of this file, via any medium is strictly prohibited
Proprietary and confidential
Written by Elijah Ethun <elijahe@gmail.com>
"""

"""
Factory responsible for creating and monitoring module thread instances.
"""

import time
import os.path
import traceback
import pkgutil

from Sven.Methods import *
from Sven.DispatchedModulesContainer import DispatchedModulesContainer
from Sven.ThreadContainer import ThreadContainer

class ModuleFactory(object):

  def __init__(self, db, config):
    self.db = db
    self.config = config
    self.events_insert = []

    self.dispatched_modules = DispatchedModulesContainer(db)
    self.threads = ThreadContainer()

    for interface in list(self.config['interfaces'].split(',')):
      notice("-" * 80)
      notice(interface)
      notice("-" * 80)

      try:
        base = __import__('Sven.Module.' + interface + '.Base')
        pkgpath = os.path.dirname(base.__file__) + '/Module/' + interface
        modules = [name for _, name, _ in pkgutil.iter_modules([pkgpath])]
        for module_name in modules:
          if module_name == 'Base':
            continue

          try:
            _name = 'Sven.Module.%s.%s' % (interface, module_name)
            _temp = __import__(_name, globals(), locals(), [module_name])

            module = getattr(_temp, module_name)

            # Skip execution if the module tells us so
            if module.module_factory_ignore == True \
                or module_name == 'Base' \
                or not getattr(module, 'dispatch'):
              continue

            # Execute the classes dispatch() method, passing in this factory
            # module, and our database. Also pass in _temp so that we can keep
            # this process DRY'd out and dynamic for modules as best as we can.
            module.dispatch(self, db, _temp)
          except:
            notice(traceback.format_exc())
      except:
        notice(traceback.format_exc())

    notice("#" * 80)
    notice("Dispatched %s modules" % len(self.dispatched_modules.modules))


  def runQueue(self):
    """
    This is run periodically from the main running process.  This executes
    queued up SQL writes since threads can't write for themselves unless they
    open up a new db connection.
    """

    if self.events_insert:
      self.insertEvents()


  def addModule(self, module):
    """
    Adds a module to our dispatched_modules container object
    """

    self.dispatched_modules.add(module)


  def addThread(self, thread):
    """
    Adds a thread to our threads container object
    """

    self.threads.add(thread)


  def queueInsertEvent(self, created, updated, message):
    """
    Queue up a database insert event when a monitor action is triggered.
    """

    data = {'created' : created, 'updated' : updated, 'message' : message}
    self.events_insert.append(data)


  def insertEvents(self):
    """
    Execute insertion of monitor events.
    """

    for index, event in enumerate(self.events_insert):
      query = "INSERT INTO monitor_event (created, updated, message, viewed) " \
                      "VALUES (%s, %s, %s, %s)"
      self.db.execute(query, (event['created'], event['updated'],
                              event['message'], False))
      self.db.commit()
      self.events_insert.pop(index)


  def checkForNewModules(self):
    """
    Threads are responsible for removing themselves from the thread pool,
    but we have to manually check for new ones here.
    """

    pass