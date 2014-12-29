#include "RCSwitch.h"
#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
     
RCSwitch mySwitch;

int main(int argc, char *argv[])
{
    int PIN = 2;
     
    if( wiringPiSetup() == -1 )
        return 0;

    mySwitch = RCSwitch();
    mySwitch.enableReceive(PIN);  // Receiver on inerrupt 0 => that is pin #2
     
    
    while( true )
    {
        if ( mySwitch.available( ) )
        {
            int value = mySwitch.getReceivedValue();
    
            if (value == 0)
            {
                printf("Unknown encoding");
            }
            else
            {
                printf("Received %i\n", mySwitch.getReceivedValue() );
            }
    
            mySwitch.resetAvailable();
        }
    }

    exit(0);
}
