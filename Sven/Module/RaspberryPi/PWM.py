"""
Copyright (C) 2014, Web Bender Consulting, LLC. - All Rights Reserved
Unauthorized copying of this file, via any medium is strictly prohibited
Proprietary and confidential
Written by Elijah Ethun <elijahe@gmail.com>
"""

from RPIO import PWM
from Sven.Module.RaspberryPi.Base import Base
from Sven.Methods import *


class PWM(Base):
  start_duty = 0
  duty = start_duty

  start_polarity = 1
  polarity = start_polarity

  start_frequency = .5
  frequency = start_frequency

  high_multiplier = 2

  pwm = None

  notes = {
    'hB' : 493.88 * high_multiplier,
    'hBb' : 466.16 * high_multiplier,
    'hAs' : 466.16 * high_multiplier,
    'hA' : 440.00 * high_multiplier,
    'hAb' : 830.61 * high_multiplier,
    'hGs' : 830.61 * high_multiplier,
    'hG' : 783.99 * high_multiplier,
    'hGb' : 739.99 * high_multiplier,
    'hFs' : 739.99 * high_multiplier,
    'hF' : 698.46 * high_multiplier,
    'hE' : 659.26 * high_multiplier,
    'hEb' : 622.25 * high_multiplier,
    'hDs' : 622.25 * high_multiplier,
    'hD' : 587.33 * high_multiplier,
    'hDb' : 554.37 * high_multiplier,
    'hCs' : 554.37 * high_multiplier,
    'hC' : 523.25 * high_multiplier,

    'B' : 493.88,
    'Bb' : 466.16,
    'As' : 466.16,
    'A' : 440.00,
    'Ab' : 830.61,
    'Gs' : 830.61,
    'G' : 783.99,
    'Gb' : 739.99,
    'Fs' : 739.99,
    'F' : 698.46,
    'E' : 659.26,
    'Eb' : 622.25,
    'Ds' : 622.25,
    'D' : 587.33,
    'Db' : 554.37,
    'Cs' : 554.37,
    'C' : 523.25
  }

  module_parameters = ['address', 'pud', 'direction']
  required_parameters = ['address', 'pud', 'direction']

  def __init__(self, module_factory = None, db = None, id = None):
    self.required_parameters = ['address']

    super(PWM, self).__init__(module_factory, db, id)
    self.address = int(self.address)

  class Meta(Meta):
    name = 'PWM Module'
    description = 'Pulse Width Modulation Output'


  def pwmStart(self):
    PWM.setup()
    PWM.init_channel(0)
    RPi.GPIO.setmode(RPi.GPIO.BCM)
    RPi.GPIO.setup(self.address, RPi.GPIO.OUT)

    self.pwm = RPi.GPIO.PWM(self.address, self.frequency)
    self.pwm.start(self.duty)


  def pwmStop(self):
    self.cleanup()


  def setFrequency(self, frequency):
    self.pwm.ChangeFrequency(frequency)


  def setDuty(self, duty):
    self.pwm.ChangeDutyCycle(duty)


  def note(self, frequency, duration = .2):
    self.setFrequency(frequency)
    time.sleep(duration)


  def playList(self, notes):
    for note in notes :
      self.note(self.notes[note])


  def cleanup(self):
    """
    cleanup method called from parent __del__ destructor.
    """

    notice("Calling cleanup in PWM")
    if self.pwm is not None :
      self.pwm.stop()


  def threadTarget(self, thread):
    while thread.running == True :
      if self.event_triggered is not None :
        self.runTriggeredEvents()

      self.runTimedUpdates(thread)
      time.sleep(.05)


  # Output state actions
  class action_soundMario(object):
    class Meta(Meta):
      name = 'Mario - Song'


    def run(self, outer, *args, **kwargs):
      outer.pwmStart()

      try :
        outer.note(outer.notes['hE'], .1)
        outer.note(1, .05)
        outer.note(outer.notes['hE'])
        outer.note(1, .05)
        outer.note(outer.notes['hE'], .15)
        outer.note(1, .1)

        outer.note(outer.notes['hC'], .1)
        outer.note(1, .05)
        outer.note(outer.notes['hE'], .15)
        outer.note(1, .05)
        outer.note(outer.notes['hG'], .1)
        outer.note(1, .4)
        outer.note(outer.notes['G'], .25)

      except :
        notice(traceback.format_exc())

      outer.pwmStop()


  class action_soundMarioCoin(object):
    class Meta(Meta):
      name = 'Mario - Coin Grab'
      description = 'Get the money!'


    def run(self, outer, *args, **kwargs):
      outer.pwmStart()

      try :
        outer.note(outer.notes['hB'] * 2, .1)
        outer.note(1, .025)
        outer.note(outer.notes['hE'] * 2, .5)

        while outer.duty > 0 :
          outer.setDuty(outer.duty)
          outer.duty = outer.duty - .5
          time.sleep(.02)

      except :
        notice(traceback.format_exc())

      outer.pwmStop()


  class action_soundMario1up(object):
    class Meta(Meta):
      name = 'Mario - 1UP'
      description = 'Not dead yet!'


    def run(self, outer, *args, **kwargs):
      outer.pwmStart()

      try :
        outer.note(outer.notes['hE'], .15)
        outer.note(outer.notes['hG'], .15)
        outer.note(outer.notes['hE'] * 2, .15)
        outer.note(outer.notes['hC'] * 2, .15)
        outer.note(outer.notes['hD'] * 2, .15)
        outer.note(outer.notes['hG'] * 2, .15)

      except :
        notice(traceback.format_exc())

      outer.pwmStop()


  class action_soundZeldaItem(object):
    class Meta(Meta):
      name = 'Zelda - Item Found'
      description = 'Surprise!'


    def run(self, outer, *args, **kwargs):
      outer.pwmStart()

      try :
        outer.note(outer.notes['hA'])
        outer.note(outer.notes['hAs'])
        outer.note(outer.notes['hB'])
        outer.note(outer.notes['hC'], 1.5)

      except :
        notice(traceback.format_exc())

      outer.pwmStop()


  class action_soundMockingJay(object):
    class Meta(Meta):
      name = 'Mocking Jay'
      description = 'Hunger Games'

    def run(self, outer, *args, **kwargs):
      outer.pwmStart()

      try :
        outer.note(outer.notes['hF'], .6)
        outer.note(outer.notes['hA'] * 2, .6)
        outer.note(outer.notes['hG'], .6)
        outer.note(outer.notes['hC'], .6)

      except :
        notice(traceback.format_exc())

      outer.pwmStop()


  class action_soundZeldaSecret(object):
    class Meta(Meta):
      name = 'Zelda - Secret Found'
      description = 'Blowed that wall up!'


    def run(self, outer, *args, **kwargs):
      outer.pwmStart()

      try :
        outer.playList(['hG', 'hFs', 'hDs', 'A', 'Gs', 'hE', 'hGs', 'hC']);

      except :
        notice(traceback.format_exc())

      outer.pwmStop()


  class action_soundNotice(object):
    class Meta(Meta):
      name = 'Standard Notice'


    def run(self, outer, *args, **kwargs):
      outer.pwmStart()

      try :
        outer.duty = 5
        timer = 1
        current = 0

        while current < timer :
          outer.setFrequency(outer.frequency)
          current = current + .2
          outer.frequency = outer.frequency + 400
          time.sleep(.02)
          outer.setFrequency(outer.frequency - 200)
          time.sleep(.02)
          outer.setFrequency(outer.frequency + 400)
          time.sleep(.02)

        outer.duty = 5

        outer.pwmStop()

      except :
        notice(traceback.format_exc())

      outer.pwmStop()


  class action_soundSiren(object):
    class Meta(Meta):
      name = 'Standard Siren'

    def run(self, outer, *args, **kwargs):
      outer.pwmStart()

      try :
        outer.frequency = 969
        timer = 2
        current = 0

        while current < timer :
          outer.setFrequency(outer.frequency)

          if outer.frequency == 800 :
            outer.frequency = 969
          else :
            outer.frequency = 800

          current = current + .5

          time.sleep(.25)

      except :
        notice(traceback.format_exc())

      outer.pwmStop()


  class action_jingleBells(object):
    class Meta(Meta):
      name = 'Jingle Bells'
      description = 'Poor Rendition'


    def run(self, outer, *args, **kwargs):
      outer.pwmStart()

      try :
        outer.note(outer.notes['hF'], )
        outer.note(1)
        outer.note(outer.notes['hF'])
        outer.note(1)
        outer.note(outer.notes['hF'], .4)
        outer.note(1)

        outer.note(outer.notes['hF'], )
        outer.note(1)
        outer.note(outer.notes['hF'])
        outer.note(1)
        outer.note(outer.notes['hF'], .4)
        outer.note(1)

        outer.note(outer.notes['hF'], )
        outer.note(1)
        outer.note(outer.notes['hA'] * 2)
        outer.note(1)
        outer.note(outer.notes['hD'])
        outer.note(1)
        outer.note(outer.notes['hE'])
        outer.note(1)

        outer.note(outer.notes['hF'], 1)

      except :
        notice(traceback.format_exc())

      outer.pwmStop()
