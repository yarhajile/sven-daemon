sven-frontend
=============

Sven is a multi-threaded daemonized Python service I wrote in an attempt to bring together disparate security / automation / control devices and services.  

This project started out as a way for me to setup my own home security system using inexpensive 433mhz wireless window / door sensors that interfaced with a Beaglebone or RaspberryPi.

I wanted to efficiently poll each window / door sensor in a close to real-time fashion which effectively became the multi-threaded process it is today.  This allows me to receive and 
act upon multiple inputs simultaneously.  

There are 3 layers to Sven from the user perspective.  Location Group, Location and Device.  Location Groups are logical groupings of locations, such as "Home" or "Office" or "Lake House".  Locations are areas within those location groups such as "Kitchen", "Garage" or "Billy's Bedroom". Devices are individual items within the Locations such as "Southeast Window" or "Closet Door".

Location groups and Locations are simple associations with only 'Name' and 'Description' parameters for each.  Device configuration is where the real magic happens and can take on many flavors.  

At their core, devices require a 'Name', 'Description', 'Interface' and 'Bus'.  Like Location Group and Location creation, 'Name' and 'Description' logically describe the device as it is used throughout the application.  

'Interface' is one of the system wide configured interfaces the daemon process will support through custom modules.  These are currently 'BeagleboneBlack', 'RaspberryPi', 'ArduinoUno', 'System' and 'Cloud'.   'BeagleboneBlack' and 'RaspberryPi' (and conceivably ArduinoUno, although not currently implemented) interfaces exist for accessing the GPIO ports on these awesome boards. 'System' is for services that run locally of the host device that act on internal components of the host machine, like sending mail, playing sounds, getting current time, etc.  'Cloud' is for cloud based services that we interface with through public API's or other means, such as interfacing with the Nest Thermostat or your home iTunes collection.

'Bus' is the device type within the interface we'll be basing our devices off of.  For the 'BeagleboneBlack' interface, this can be one of the ports for GPIO, PWM, I2C, UART, etc.  In the case of the 'Cloud' interface, this can be a host 'Nest Account' ( with related Nest Thermostat and / or Nest Protect modules referencing the account ) or your MyQ enabled garage door opener.

'Device' level configuration is where we set device specific values such as username / password / api key, etc. for cloud based bus types or address information for GPIO / PWM, etc. style busses.  Additionally, once the device specific parameters are configured, we can configure actions that will occur when the device is triggered ( if it is an 'input' device ) and optionally any conditions that must be met before said action is performed. 

The actions these devices can perform are derived from the module definitions and can be customized infinitely as all output actions have knowledge through the module factory of what every other module in the system is up to as well as having the ability to perform their own actions outside of Sven.

I set it up in such a way that a device could act in 3 different states; input, output, both.  This allows me to intelligently and dynamically perform actions when an input action occurs. Devices can be anything from physical hardware inputs on GPIO ports, software-based email notifications, cloud based actions (set the temperature on your Nest Thermostat?) or even a device established for updating a twitter feed.

Additionally, device actions are dependent on conditions you establish for the modules in the web-based configuration panel.

Consider the following 5 device configuration.
	* A 433mhz wireless sensor attached do your front door.
	* A siren attached to pin P8_17 on your BeagleboneBlack.
	* A Nest Thermostat.
	* Alarm.
	* SMS Notification.

Scenario A
	FRONT DOOR SWITCH blares the SIREN when the NEST THERMOSTAT indoor temperature is less than 74F and the ALARM is in the 'away' state.

Scenario B
    When the NEST THERMOSTAT rises above 80F chirps the SIREN and sends an SMS NOTIFICATION.

Scenario C
    FRONT DOOR SWITCH silently triggers the SMS NOTIFICATION when the ALARM is in the 'home' state and the current time is between 8:00PM and 8:00AM.


The biggest problem I saw with other automation and control systems is that you were tied to their own specific interface that only worked with devices for that particular service.  I wanted a one-stop-shop to control this behavior in a modular fashion and this is where the idea for Sven came from.  I have no prior experience in automation / control systems and as a personal experiment I intentionally chose to not look into other systems that might be performing in a similar way in an effort to come up with a system that fit my needs and wants. 

At its core is the ModuleFactory which is responsible for dispatching the various module device instances and bringing them together under one roof.

Each module instance operates in its own thread and can communicate with any other thread through this ModuleFactory umbrella.

Modules can be instantiated as many times as necessary under the ModuleFactory umbrella with varying parameters.

Modules provide a set of conditions that when configured and added through the front-end interface, must be met on the back-end before any action elements ( when in an output state ) can be performed. 

All output action elements inside the modules provide meta information about themselves to the front-end for better display of names, descriptions and other custom elements.

Multiple output action elements in a module can be chained together on an input action. Note that these actions occur asyncronously with other modules, so collisions may occur.  As is in the case of multiple devices competing for sound output through the default system audio component.

Execution of device output actions where conditions have been configured on the front-end are inclusive vs. exclusive, meaning that if any action condition is TRUE, then the action will trigger.  This feature is under development and likely to change.

One area I've regrettably not given recent attention to is the alarm system module.  Initially, the alarm system was a hard-coded component of the callback() function but as the modularized system evolved, the hard-coded nature of the alarm system was yarded out so that it could be just another module.  One tricky area that I've not addressed is how to incorporate this dynamic alarm module at the location and location group levels.  While it is conceivable to set output action conditions on each and every device when it comes to setting the alarm module's status, a way to set this carte blanche at the Location or Location Group level or even user-definable device groupings would be ideal. 
