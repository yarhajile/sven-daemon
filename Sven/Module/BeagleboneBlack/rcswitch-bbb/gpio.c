#include <stdio.h>
#include <unistd.h>
#include <stdint.h>
#include <time.h>


#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <unistd.h>
#include <fcntl.h>
#include <poll.h>


#include <sys/time.h>
#include <pthread.h>

#include "gpio.h"

void pinMode(uint8_t bPin, uint8_t bMode)
{
    // First try to open Direction
    FILE *pfileDir;
    char abT[34];

    sprintf(abT, "/sys/class/gpio/gpio%d/direction", bPin);
    pfileDir = fopen(abT, "w");
   
    if (pfileDir == NULL)
    {
        // Probably not exported...
        FILE *pfileExport = fopen("/sys/class/gpio/export", "w");
        if(pfileExport == NULL)  
        {
            printf("Unable to open export.\n");
            return;
        }
        fseek(pfileExport, 0, SEEK_SET);
        fprintf(pfileExport, "%d", bPin);
        fflush(pfileExport);
        fclose(pfileExport);
           
        // Again lets try to open the file direction
        pfileDir = fopen(abT, "w");
        if (pfileDir == NULL)
        {
            printf("Error opening: %s\n", abT);
            return;
        }    
    }
   
    fseek(pfileDir, 0, SEEK_SET);
    switch (bMode)
    {
        case INPUT:
            fprintf(pfileDir, "in");
            break;
        case OUTPUT:
            fprintf(pfileDir, "out");
            break;
        case INPUT_PULLUP:
            // BUGBUG:: Have not done anything with pull up yet...
            fprintf(pfileDir, "in");
            break;
    }        
    fflush(pfileDir);
    fclose(pfileDir);
}    
   

// We will cache out one pin for now... Probably not much use, but...
static uint8_t s_bDWPinLast = 0xff;
static FILE * s_pfileDW = NULL;

void digitalWrite(uint8_t bPin, uint8_t bVal)
{
    char abT[32];
    // This function assumes that pinMode was called, which made sure things were exported...
    if (bPin != s_bDWPinLast)
    {
        if (s_pfileDW)
        {
            fclose(s_pfileDW);
        }
        sprintf(abT, "/sys/class/gpio/gpio%d/value", bPin);
        s_pfileDW = fopen(abT, "w");
        if (s_pfileDW == NULL)
        {
            s_bDWPinLast = 0xff;
            printf("error opening %s\n", abT);
            return;
        }
        s_bDWPinLast = bPin;
    }
    fseek(s_pfileDW, 0, SEEK_SET);
    fprintf(s_pfileDW, "%d\n", (int)bVal);
    fflush(s_pfileDW);
       
}
    
void release_gpios() {
    s_bDWPinLast = 0xff;
    if (s_pfileDW)
    {
        fclose(s_pfileDW);
    }
    s_pfileDW = NULL;
}

char abT[32];
int digitalRead(uint8_t bPin)
{
    
    // This function assumes that pinMode was called, which made sure things were exported...
    if (bPin != s_bDWPinLast)
    {
        if (s_pfileDW)
        {
            fclose(s_pfileDW);
        }
        sprintf(abT, "/sys/class/gpio/gpio%d/value", bPin);
        s_pfileDW = fopen(abT, "r");
        if (s_pfileDW == NULL)
        {
            s_bDWPinLast = 0xff;
            printf("error opening %s\n", abT);

            return -1;

        }
        s_bDWPinLast = bPin;
    } else {
        //printf(abT);
        fclose(s_pfileDW);
        s_pfileDW = fopen(abT, "r");
    }
    //fseek(s_pfileDW, 0, SEEK_SET);

    int iRet = fgetc(s_pfileDW);
    if (iRet == '0')
        return 0;
    if (iRet == '1')
        return 1;
    return iRet;  // ?????
}

unsigned long millis(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC,  &ts );
    return ( ts.tv_sec * 1000 + ts.tv_nsec / 1000000L );
}


unsigned long micros(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts );
    return ( ts.tv_sec * 1000000L + ts.tv_nsec / 1000L );
}

static uint64_t epochMilli, epochMicro ;

/*
 * millis:
 *	Return a number of milliseconds as an unsigned int.
 *********************************************************************************
 */
 
void initialiseEpoch (void)
{
  struct timeval tv ;

  gettimeofday (&tv, NULL) ;
  epochMilli = (uint64_t)tv.tv_sec * (uint64_t)1000    + (uint64_t)(tv.tv_usec / 1000) ;
  epochMicro = (uint64_t)tv.tv_sec * (uint64_t)1000000 + (uint64_t)(tv.tv_usec) ;
}

unsigned int epoch_millis (void)
{
  struct timeval tv ;
  uint64_t now ;

  gettimeofday (&tv, NULL) ;
  now  = (uint64_t)tv.tv_sec * (uint64_t)1000 + (uint64_t)(tv.tv_usec / 1000) ;

  return (uint32_t)(now - epochMilli) ;
}


/*
 * micros:
 *	Return a number of microseconds as an unsigned int.
 *********************************************************************************
 */

unsigned int epoch_micros (void)
{
  struct timeval tv ;
  uint64_t now ;

  gettimeofday (&tv, NULL) ;
  now  = (uint64_t)tv.tv_sec * (uint64_t)1000000 + (uint64_t)tv.tv_usec ;

  return (uint32_t)(now - epochMicro) ;
}

#define SYSFS_GPIO_DIR "/sys/class/gpio"
#define POLL_TIMEOUT (3 * 1000) /* 3 seconds */
#define MAX_BUF 64


/****************************************************************
 * gpio_export
 ****************************************************************/
int gpio_export(unsigned int gpio)
{
	int fd, len;
	char buf[MAX_BUF];
 
	fd = open(SYSFS_GPIO_DIR "/export", O_WRONLY);
	if (fd < 0) {
		perror("gpio/export");
		return fd;
	}
 
	len = snprintf(buf, sizeof(buf), "%d", gpio);
	write(fd, buf, len);
	close(fd);
 
	return 0;
}

/****************************************************************
 * gpio_unexport
 ****************************************************************/
int gpio_unexport(unsigned int gpio)
{
	int fd, len;
	char buf[MAX_BUF];
 
	fd = open(SYSFS_GPIO_DIR "/unexport", O_WRONLY);
	if (fd < 0) {
		perror("gpio/export");
		return fd;
	}
 
	len = snprintf(buf, sizeof(buf), "%d", gpio);
	write(fd, buf, len);
	close(fd);
	return 0;
}

/****************************************************************
 * gpio_set_dir
 ****************************************************************/
int gpio_set_dir(unsigned int gpio, unsigned int out_flag)
{
	int fd, len;
	char buf[MAX_BUF];
 
	len = snprintf(buf, sizeof(buf), SYSFS_GPIO_DIR  "/gpio%d/direction", gpio);
 
	fd = open(buf, O_WRONLY);
	if (fd < 0) {
		perror("gpio/direction");
		return fd;
	}
 
	if (out_flag)
		write(fd, "out", 4);
	else
		write(fd, "in", 3);
 
	close(fd);
	return 0;
}


/****************************************************************
 * gpio_set_edge
 ****************************************************************/

int gpio_set_edge(unsigned int gpio, char *edge)
{
	int fd, len;
	char buf[MAX_BUF];

	len = snprintf(buf, sizeof(buf), SYSFS_GPIO_DIR "/gpio%d/edge", gpio);
 
	fd = open(buf, O_WRONLY);
	if (fd < 0) {
		perror("gpio/set-edge");
		return fd;
	}
 
	write(fd, edge, strlen(edge) + 1); 
	close(fd);
	return 0;
}

/****************************************************************
 * gpio_fd_open
 ****************************************************************/

int gpio_fd_open(unsigned int gpio)
{
	int fd, len;
	char buf[MAX_BUF];

	len = snprintf(buf, sizeof(buf), SYSFS_GPIO_DIR "/gpio%d/value", gpio);
 
	fd = open(buf, O_RDONLY | O_NONBLOCK );
	if (fd < 0) {
		perror("gpio/fd_open");
	}
	return fd;
}

/****************************************************************
 * gpio_fd_close
 ****************************************************************/

int gpio_fd_close(int fd)
{
	return close(fd);
}

struct gpio_isr_struct {
    int pin;
    void (*func)(void);
};

void* launch_func(void *arguments) {
    struct gpio_isr_struct *args = arguments;
    (void) (*(args->func))();
}

void* checkGPIO(void *arguments) {
    /*int err;
    pthread_t thread_id;
    struct gpio_isr_struct *args = arguments;
    void (*function_pointer)();
    
    int pin = args->pin;
    function_pointer = args->func;
    
    uint8_t nval;
    uint8_t last_val = digitalRead(pin);
    while(true) {
        nval = digitalRead(pin);
        if (nval != last_val) {
            last_val = nval;
            pthread_create(&thread_id, NULL, &launch_func, (void *)args);
            //(void) (*function_pointer)();
        }
        //usleep(1);
    }*/
    
	struct pollfd fdset[2];
	int nfds = 2;
	int gpio_fd, timeout, rc;
	char *buf[MAX_BUF];
	int len;
	
    struct gpio_isr_struct *args = arguments;
    void (*function_pointer)();
    
    int pin = args->pin;
    function_pointer = args->func;
    
    gpio_export(args->pin);
	gpio_set_dir(args->pin, 0);
	gpio_set_edge(args->pin, "both");
	gpio_fd = gpio_fd_open(args->pin);
	
	timeout = POLL_TIMEOUT;
	
	while (1) {
		memset((void*)fdset, 0, sizeof(fdset));

		fdset[0].fd = STDIN_FILENO;
		fdset[0].events = POLLIN;
      
		fdset[1].fd = gpio_fd;
		fdset[1].events = POLLPRI;

		rc = poll(fdset, nfds, timeout);      

		if (rc < 0) {
			printf("\npoll() failed!\n");
			return -1;
		}
		
		if (rc == 0) {
		    //printf(".");
		}
            
		if (fdset[1].revents & POLLPRI) {
			len = read(fdset[1].fd, buf, MAX_BUF);
			(void) (*function_pointer)();
			//printf("\npoll() GPIO %d interrupt occurred\n", args->pin);
		}

		if (fdset[0].revents & POLLIN) {
			(void)read(fdset[0].fd, buf, 1);
			//printf("\npoll() stdin read 0x%2.2X\n", (unsigned int) buf[0]);
		}

		//printf(".");
		fflush(stdout);
	}

	gpio_fd_close(gpio_fd);
	return 0;
}
 
int GPIOISR (int pin, int mode, void (*function)(void))
{
    int err;
    pthread_t thread_id;
    
    //struct gpio_isr_struct *args;
    struct gpio_isr_struct *args =
        (struct gpio_isr_struct*) calloc(1, sizeof(*args));
    args->pin = pin;
    args->func = function;
    
    err = pthread_create(&thread_id, NULL, &checkGPIO, (void *)args);
}

