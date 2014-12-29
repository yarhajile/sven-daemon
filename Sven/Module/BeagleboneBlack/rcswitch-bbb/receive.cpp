#include "RCSwitch.h"
#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>

int main() {
    int PIN = 30; //BCM 18, GPIO1

    //if (wiringPiSetup () == -1) return 1;
    initialiseEpoch();
    
    RCSwitch mySwitch = RCSwitch();

    pinMode(PIN, INPUT);
    
    mySwitch.enableReceive(PIN);
    
    printf("enabled");

    while( true )
    {
        if (mySwitch.available())
        {
            printf("available\n");
            printf("%lu\n",mySwitch.getReceivedValue());
            mySwitch.resetAvailable();
        }
        
        usleep(1000);
    }

    return(0);
}

