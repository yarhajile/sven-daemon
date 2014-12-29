"""
Copyright (C) 2014, Web Bender Consulting, LLC. - All Rights Reserved
Unauthorized copying of this file, via any medium is strictly prohibited
Proprietary and confidential
Written by Elijah Ethun <elijahe@gmail.com>
"""

"""
Stores our exception definitions.
"""

import sys
import syslog
import smtplib
import exceptions

class ConditionException( exceptions.Exception ):
  pass


class AlertException (exceptions.Exception):
  """
  Class for sending exception messages to SMTP recipients.
  """

  def __init__(self, message, alert = True):
    self.message = message

    if alert:
      self.alert()


  def __str__(self):
    return self.message


  def alert(self):
    """
    Send a basic error notification to SMTP recipients.
    """

    global config

    for address in config['alert_recipients']:
      message =  "To: <%s>\n" % (address,)
      message += "From: <%s>\n" % (config['alert_sender'],)
      message += "Subject: SVEN-NOTIFICATION: Backend script error!"
      message += "\n"
      message += "An error has occurred with the backend script '%s'\n" % (sys.argv[0],)
      message += "  Message: %s" % (self.message,)

      try:
        smtp = smtplib.SMTP()
        smtp.connect( config['alert_smtp_host'], config['alert_smtp_port'] )

        if config['smtp_user'] and config['smtp_pass']:
          smtp.login(config['smtp_user'], config['smtp_pass'])

        smtp.sendmail( config['alert_sender'], address, message)
        smtp.quit()
      except smtplib.SMTPException as ex:
        syslog.syslog("Failed to send SMTP exception alert to recipient %s: %s." % ( address, ex, ) )


class RequestException(exceptions.Exception):
    pass
