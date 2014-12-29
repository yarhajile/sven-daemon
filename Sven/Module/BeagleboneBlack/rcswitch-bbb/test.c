#include <stdio.h>
#include <unistd.h>
#include <stdint.h>
#include <time.h>
#include "gpio.h"

int main(int argc, const char *argv[])
{

    printf("Start Test IO Pin\n\r");

    pinMode(60, OUTPUT);      // set our pin as output
    
    while(true) {
        digitalWrite(60, HIGH);
        usleep(10);
        digitalWrite(60, LOW);
        usleep(10);
    }
    return 0;
}
