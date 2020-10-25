# ***VERSION 2***
This is mostly unstable right now, I am doing a lot of rewrites.
Right now it is working for me, but I would love some feedback.

***MOST*** of the time, this script ***WILL NOT*** work.
Please feel free to browse the code and give me ideas for smoother opperation.

# Personal Thermostat
Idea of building a smart thermostat with a raspberry pi or arduino.  Either way, it needs the same interfaces and such.

## Basic Concept
Use a raspberry pi or an arduino or a combination of several to provide a "Smart Thermostat" for my home.
I would like use a tablet as a visual interface that shows a self hosted web page.
This way, I can do modifications from a central computer, (my laptop), and access the thermostat from afar.
I also want the settings, even simple temp adjustment, to require administrative privileges.  (I have kids!!)

### Why Not Buy One
First reason would be that I have a hard time spending money on things that I don't actually control.
There are several "Smart Items" that the company have gone out of business and the App's they provide are now null.
Even well known items such at ["NEST"](https://store.google.com/us/magazine/compare_thermostats?hl=en-US&GoogleNest&utm_source=nest_redirect&utm_medium=google_oo&utm_campaign=GS103056&utm_term=thermostats), which you can access with things such as [OpenHAB](https://www.openhab.org/), are closed source, and I would much rather stick with open source hardware and software.
Next, if I was just going to go buy one, what is the fun in that?

### Web interface
What does this need to show?  Who can adjust it?

  * Indoor temp
  * Outdoor temp
  * Projected high/low temp
  * Current setting
  * Adjust buttons  - Password protected

### Control functions
What does this need to do?

  * Poll an outdoor temp sensor, or weather API
  * Poll multiple indoor temp sensors to get an average temp
  * Get current desired setting
  * Poll for occupancy
    1.  Ping for WiFi
    2.  Ping for Bluetooth
    3.  Check motion detectors
  * Check configuration for specific settings
    1.  Should it stay activated
    2.  Should it turn on or off at specific time
    3.  Should it be heating or cooling

#### More Notes
