"""
Copyright (C) 2014, Web Bender Consulting, LLC. - All Rights Reserved
Unauthorized copying of this file, via any medium is strictly prohibited
Proprietary and confidential
Written by Elijah Ethun <elijahe@gmail.com>
"""

"""
DispatchedModulesContainer.py

This class dispatches and tracks modules.
"""

import time
import os.path
import traceback
import pkgutil

from Sven.Methods import *

class DispatchedModulesContainer(object):
  def __init__(self, db):
    self.modules = {}
    self.db = db


  def add(self, module):
    module_name = module.__class__.__name__

    if not module_name in self.modules:
      self.modules[module_name] = []

    self.modules[module_name].append(module)


  def getAllOutputDevices(self):
    deviceList = []

    for module_name, module_items in self.modules.items():
      for device_details in module_items:
        if hasattr(device_details, 'devices'):
          for device in device_details.devices:
            if device.direction == 1 \
                or device.direction == 'out' \
                or device.direction == 'both':
              deviceList.append(device)
        else:
          if device_details.direction == 1 \
              or device_details.direction == 'out' \
              or device_details.direction == 'both':
            deviceList.append(device_details)
    return deviceList


  def getAllInputDevices(self):
    deviceList = []

    for module_name, module_items in self.modules.items():
      for device_details in module_items:
        if hasattr(device_details, 'devices'):
          for device in device_details.devices:
            if device.direction == 0 or device.direction == 'in':
              deviceList.append(device)
        else:
          if device_details.direction == 0 or device_details.direction == 'in':
            deviceList.append(device_details)
    return deviceList


  def getAllDevices(self):
    deviceList = []

    for module_name, module_items in self.modules.items():
      for device_details in module_items:
        if hasattr(device_details, 'devices'):
          for device in device_details.devices:
            deviceList.append(device)
        else:
          deviceList.append(device_details)
    return deviceList


  def getDeviceById(self, device_id):
    device_id = int(device_id)
    for module_name, module_items in self.modules.items():
      for device_details in module_items:
        if hasattr(device_details, 'devices'):
          for device in device_details.devices:
            if device.id == device_id:
              return device
        else:
          if device_details.id == device_id:
            return device_details


  def getDeviceByName(self, interface, bus):
    for module_name, module_items in self.modules.items():
      if module_name == interface:
        for device_details in module_items:
          if hasattr(device_details, 'devices'):
            for device in device_details.devices:
              if device.deviceType == bus:
                return device
          else:
            if device_details.deviceType == bus:
              return device_details
