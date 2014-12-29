/*
  Morse.h - Library for Livolo wireless switches.
  Created by Sergey Chernov, October 25, 2013.
  Released into the public domain.
*/

#include "RCSwitch.h"

#ifndef Livolo_h
#define Livolo_h

extern void pinMode(uint8_t bPin, uint8_t bMode);
extern void digitalWrite(uint8_t bPin, uint8_t bVal);

#define bitRead(value, bit) (((value) >> (bit)) & 0x01)

class Livolo
{
  public:
    Livolo(uint8_t pin);
    void sendButton(uint16_t remoteID, byte keycode);
  private:
    uint8_t txPin;
	byte i; // just a counter
	byte pulse; // counter for command repeat
	boolean high; // pulse "sign"
	void selectPulse(byte inBit);
	void sendPulse(byte txPulse);
};

#endif
