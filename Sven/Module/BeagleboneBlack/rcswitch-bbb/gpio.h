#include <stdint.h>

#ifndef __GPIO_H__
#define __GPIO_H__

#define HIGH 0x1
#define LOW  0x0

#define INPUT 0x0
#define OUTPUT 0x1
#define INPUT_PULLUP 0x2

#define true 0x1
#define false 0x0

static uint64_t epochMilli, epochMicro ;

void pinMode(uint8_t bPin, uint8_t bMode);
void digitalWrite(uint8_t bPin, uint8_t bVal);
int digitalRead(uint8_t bPin);
void release_gpios();


unsigned long millis (void);
unsigned long micros (void);

int GPIOISR (int pin, int mode, void (*function)(void));

unsigned int epoch_micros (void);
unsigned int epoch_millis (void);
void initialiseEpoch (void);

#endif
