"""
Copyright (C) 2014, Web Bender Consulting, LLC. - All Rights Reserved
Unauthorized copying of this file, via any medium is strictly prohibited
Proprietary and confidential
Written by Elijah Ethun <elijahe@gmail.com>
"""
from Sven.Module.ModuleBase import ModuleBase
from Sven.Methods import *

class Base (ModuleBase):
  class InterfaceMeta(InterfaceMeta):
    name = 'Cloud Interface'
    description = 'Cloud based devices'