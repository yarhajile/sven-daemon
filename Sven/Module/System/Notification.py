"""
Copyright (C) 2014, Web Bender Consulting, LLC. - All Rights Reserved
Unauthorized copying of this file, via any medium is strictly prohibited
Proprietary and confidential
Written by Elijah Ethun <elijahe@gmail.com>
"""

import smtplib

from Sven.Module.System.Base import Base
from Sven.Methods import *

class Notification(Base) :
  """
  Notification service
  """

  module_parameters = []
  required_parameters = []


  class Meta(Meta) :
    name = 'Notification'
    description = 'Sends out notifications to peeps in the config'


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
      time.sleep(1) # Not much to do here, so only loop once a second.


  def getTime(self) :
    return time.time()


  def showFullTime(self) :
    return time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())


  def email(self, toAddress = None) :
    if toAddress is None :
      toAddress = self.config.toAddresses

    message = 'New notification from Sven at ' + self.showFullTime() + '\n\n'

    server = smtplib.SMTP(self.config.smtpServer)
    server.starttls()
    server.login(self.config.username, self.config.password)
    server.sendmail(self.config.fromAddress, toAddress, message)
    server.quit()


  class action_Email(object) :
    class Meta(Meta) :
      name = 'Email'


    def run(self, outer, *args, **kwargs) :
      outer.email()


  class action_SMS(object) :
    """
    Carrier Email to SMS Gateway

    *****************************************************************

    Alltel [10-digit phone number]@message.alltel.com
    Example: 1234567890@message.alltel.com

    AT&T (formerly Cingular) [10-digit phone number]@txt.att.net
    [10-digit phone number]@mms.att.net (MMS)
    [10-digit phone number]@cingularme.com
    Example: 1234567890@txt.att.net

    Boost Mobile [10-digit phone number]@myboostmobile.com
    Example: 1234567890@myboostmobile.com

    Nextel (now Sprint Nextel) [10-digit telephone number]@messaging.nextel.com
    Example: 1234567890@messaging.nextel.com

    Sprint PCS (now Sprint Nextel) [10-digit phone number]@messaging.sprintpcs.com
    [10-digit phone number]@pm.sprint.com (MMS)
    Example: 1234567890@messaging.sprintpcs.com

    T-Mobile [10-digit phone number]@tmomail.net
    Example: 1234567890@tmomail.net

    US Cellular [10-digit phone number]email.uscc.net (SMS)
    [10-digit phone number]@mms.uscc.net (MMS)
    Example: 1234567890@email.uscc.net

    Verizon [10-digit phone number]@vtext.com
    [10-digit phone number]@vzwpix.com (MMS)
    Example: 1234567890@vtext.com

    Virgin Mobile USA [10-digit phone number]@vmobl.com
    Example: 1234567890@vmobl.com

    *****************************************************************
    """

    class Meta(Meta) :
      name = 'Email'

    def run(self, outer, *args, **kwargs) :
      outer.email(self.config.sms)
