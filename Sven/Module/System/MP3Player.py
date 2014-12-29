"""
Copyright (C) 2014, Web Bender Consulting, LLC. - All Rights Reserved
Unauthorized copying of this file, via any medium is strictly prohibited
Proprietary and confidential
Written by Elijah Ethun <elijahe@gmail.com>
"""

from Sven.Module.System.Base import Base
from Sven.Methods import *


class MP3Player(Base) :
  module_parameters = ['player']
  required_parameters = ['player']


  def __init__(self, module_factory = None, db = None, id = None) :
    super(MP3Player, self).__init__(module_factory, db, id)
    self.direction = 'out'


  class Meta(Meta) :
    name = 'MP3 Player'
    description = 'Plays files via audio output device'


  def threadTarget(self, thread) :
    """
    This method is the thread 'target' called from the parent addThread()
    method. The parent addThread() method is typically called from our static
    dispatch method.
    """

    while thread.running == True :
      if self.event_triggered is not None :
        self.runTriggeredEvents()

      self.runTimedUpdates(thread)
      time.sleep(.05)


  def play(self, file) :
    notice("Playing: %s media/%s > /dev/null 2>&1" % ( self.player, file ))
    os.system("%s media/%s > /dev/null 2>&1" % ( self.player, file ))


  class action_GarageDoor(object) :
    class Meta(Meta) :
      name = 'Garage Door'

    def run(self, outer, *args, **kwargs) :
      outer.play("garage_door.mp3")


  class action_KitchenWindow(object) :
    class Meta(Meta) :
      name = 'Kitchen Window'

    def run(self, outer, *args, **kwargs) :
      outer.play("kitchen_window.mp3")


  class action_PatioDoor(object) :
    class Meta(Meta) :
      name = 'Patio Door'

    def run(self, outer, *args, **kwargs) :
      outer.play("patio_door.mp3")


  class action_EastFamilyRoomWindow(object) :
    class Meta(Meta) :
      name = 'East Family Room Window'

    def run(self, outer, *args, **kwargs) :
      outer.play("east_family_room_window.mp3")


  class action_WestFamilyRoomWindow(object) :
    class Meta(Meta) :
      name = 'West Family Room Window'

    def run(self, outer, *args, **kwargs) :
      outer.play("west_family_room_window.mp3")


  class action_NorthLivingRoomWindow(object) :
    class Meta(Meta) :
      name = 'North Living Room Window'

    def run(self, outer, *args, **kwargs) :
      outer.play("north_living_room_window.mp3")


  class action_WestLivingRoomWindow(object) :
    class Meta(Meta) :
      name = 'West Living Room Window'

    def run(self, outer, *args, **kwargs) :
      outer.play("west_living_room_window.mp3")


  class action_FrontDoor(object) :
    class Meta(Meta) :
      name = 'Front Door'

    def run(self, outer, *args, **kwargs) :
      outer.play("front_door.mp3")


