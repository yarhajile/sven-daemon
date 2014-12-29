/*
 Usage: ./send <systemCode> <unitCode> <command>
 Command is 0 for OFF and 1 for ON
 */

#include "livolo.h"
#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>

#include <sys/time.h>
#include <sys/resource.h>

#include <pthread.h>
#include <sched.h>

void set_realtime_priority() {
    int ret;
 
    // We'll operate on the currently running thread.
    pthread_t this_thread = pthread_self();
    // struct sched_param is used to store the scheduling priority
    struct sched_param params;
    // We'll set the priority to the maximum.
    params.sched_priority = sched_get_priority_max(SCHED_FIFO);
    
    //std::cout << "Trying to set thread realtime prio = " << params.sched_priority << std::endl;
 
    // Attempt to set thread real-time priority to the SCHED_FIFO policy
    ret = pthread_setschedparam(this_thread, SCHED_FIFO, &params);
    if (ret != 0) {
        // Print the error
        printf("Unsuccessful in setting thread realtime prio");
        return;
    }
}

int main(int argc, char *argv[]) {

    //setpriority(PRIO_PROCESS, 0, -20);
    set_realtime_priority();
    
    int PIN = 60;
    uint16_t remoteCode = atoi(argv[1]);
    byte command = atoi(argv[2]);
    
    Livolo livolo(PIN); // transmitter connected to pin #8
    //while(true) {
        printf("sending remote[%i] command[%i]\n", remoteCode, command);
        livolo.sendButton(remoteCode, command); // blink button #3 every 3 seconds using remote with remoteID #6400
    //}
    /*uint16_t remoteCode = 6400;
    byte command = 0;

    pinMode(PIN, OUTPUT);      // set our pin as output
    
    //if (wiringPiSetup () == -1) return 1;
	printf("sending systemCode[%i] command[%i]\n", remoteCode, command);
	RCSwitch mySwitch = RCSwitch();
	mySwitch.enableTransmit(PIN);
	mySwitch.sendButton(remoteCode, command);*/
    /*switch(command) {
        case 1:
            mySwitch.sendButton(systemCode, unitCode);
            mySwitch.sendButton(systemCode, unitCode);
            break;
        case 0:
            mySwitch.sendButton(systemCode, unitCode);
            mySwitch.sendButton(systemCode, unitCode);
            break;
        default:
            printf("command[%i] is unsupported\n", command);
            return -1;
    }*/
	return 0;
}

