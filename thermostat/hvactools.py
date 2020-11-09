# Miscelanous tools to help with various processing

import logging
import urllib.request
import json
import pathlib
from pathlib import Path
import datetime
import time

import paho.mqtt.client as mqtt

LOGGER = logging.getLogger("__main__.tools")
LOGGER.debug("Loading hvactools")

class TimedObject():
    """
    Used as a subclass for any object that needs something done on a schedule

    :param => delayTime => An intiger in seconds describing how often to update

    :properties
        :private
            __defaultDelay => Used to reset object timer to origional setting
            __lastCheck => A datetime object to compare current time with
        :public
            delay => This can be changed by the user and resets to default after
                the alloted time

    :methods
        shouldUpdate => Returns True if enough time has passed for the update
        update => Override this function in the child class.
            Commands to execute when the timer is up
    """

    def __init__(self, delayTime):
        """:param => delayTime => int in seconds used as the defalut delay time """

        self.LOGGER = logging.getLogger("__main__.Tools.TimedObject")
        self.__defaultDelay = delayTime
        self.delay = self.defaultDelay
        self.__lastCheck = None

    @property
    def lastCheck(self):
        return self.__lastCheck

    @lastCheck.setter
    def lastCheck(self, newTime):
        self.__lastCheck = newTime

    @property
    def defaultDelay(self):
        return self.__defaultDelay

    def shouldUpdate(self):
        """Returns True if the delay time in seconds has passed.  Else returns False"""
        try:
            if datetime.datetime.now() > self.lastCheck + datetime.timedelta(minutes=self.delay):
                return True
            return False
        except TypeError as e:
            if self.lastCheck == None:
                self.lastCheck = datetime.datetime.now()
                return True
        return False

    def update():
        """
        This function should be overridden in Child class
        """
        pass

class MQTTClient():
    def __init__(self, name=None, host="localhost", port=1883, keepalive=60, bind_address=""):
        self.name = name
        self.host = host
        self.port = port
        self.LOGGER = logging.getLogger("__main__.tools.MQTTClient")
        self.client = mqtt.Client(self.name)
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message

        self.__enabled = False

        self.desiredTemp = None
        # self.client.on_connect = self.onConnect
        self.client.connect(host, port, keepalive, bind_address)
        # self.client.loop_start()
        # time.sleep(1)

    @property
    def enabled(self):
        return self.__enabled

    @enabled.setter
    def enabled(self, value):
        self.__enabled = value

    def on_connect(self, client, userdata, flags, rc):
        self.enabled = True
        self.client.subscribe("ziggy/climate/temp/desired")
        if rc == 0:
            pass

    def on_disconnect(self):
        self.enabled = False

    def start(self):
        self.client.loop_start()
        time.sleep(1)

    def stop(self):
        self.client.loop_stop()
        time.sleep(1)

    def publish(self, topic, message, qos=1, retain=True):
        if self.enabled:
            self.client.publish(topic, message, qos, retain)
        else:
            self.LOGGER.error("MQTT server not connected at {} port {}".format(self.host, self.port))

    def on_message(self, client, userdata, msg):
        message = {}
        if msg.topic == "ziggy/climate/temp/desired":
            message = str(msg.payload.decode())
            self.LOGGER.debug(message)
            self.desiredTemp = int(message)

def loadSettings(jsonFile):
    # Convert filename to python path
    try:
        jsonFile = Path(jsonFile)
    except Error as e:
        LOGGER.error(e)
    DICT = None
    try:
        with open(jsonFile, "r") as jfile:
            DICT = json.load(jfile)
    except ValueError as e:
        LOGGER.error("JSON file {} did not load.  Check format.".format(jsonFile))
    return DICT

def updateSettings(oldSettings, newSettings):
    """
    oldSettings => Either a python dictionary or None
    settings => can either be a valid json file, or a python dictionary
    """
    DICT = None
    def update(old, new):
        for setting, value in new.items():
            if setting in old and old[setting] != new[setting]:
                old[setting] = new[setting]
            else:
                LOGGER.debug("{} is not a valid setting".format(setting))
        return old

    # Check if newSettings is a json file or a dictionary
    # Convert filename to python path
    try:
        jsonFile = Path(newSettings)
    except Error as e:
        LOGGER.error("Error updating settings {}".format(e))
    try:
        with open(jsonFile, "r") as jfile:
            DICT = json.load(jfile)
    except ValueError as e:
        if type(newSettings) == type(dict):
            DICT = newSettings
    if oldSettings:
        return update(oldSettings, DICT)
    else:
        return DICT

# def checkUserConfig(configFile):
#     if Path.exists(configFile):
#         return True

#########################################
# Logic section
#########################################

# def setThermostatState(highTemp, lowTemp, desiredTemp):
#     LOGGER = logging.getLogger("__main__.tools.setThermostatState")
#     LOGGER.debug("hTemp: {}  lTemp: {}  dTemp: {}".format(highTemp, lowTemp, desiredTemp))
#     date = datetime.date.today()
#     # Summer time
#     if date.month > 4 and date.month < 9:
#         if highTemp > desiredTemp:
#             LOGGER.debug("summer time")
#             return "COOL"
#     # Winter time
#     elif date.month > 9 and date.month < 4:
#         if lowTemp < desiredTemp:
#             LOGGER.debug("winter time")
#             return "HEAT"
#     # In between time
#     elif highTemp > desiredTemp + 15 and lowTemp < desiredTemp - 15:
#         LOGGER.info("you must live in colorado")
#     elif highTemp > desiredTemp + 10:
#         # Turn cool on
#         LOGGER.debug("In between cool on")
#         return "COOL"
#     elif lowTemp < desiredTemp - 10:
#         # Turn heat on
#         LOGGER.debug("In between heat on")
#         return "HEAT"
#     LOGGER.debug("NO ALTERATIONS")
#     return "OFF"

# def setDesiredTemp(settings, time):
#     """
#     settings => A dictionary of conditions with modifiers attached
#     time => The time of day in 24 hr format
#     """
#     dTemp = settings["DEFAULT_TEMP"]
#     for t in settings["TIME_SETTINGS"].values():
#         if time >= t[0] and time <= t[1]:
#             dTemp += t[2]

# def checkTimeDelay(time1, time2, delay):
#     if time2 == None:
#         print("True None")
#         return True
#     tdelay = time2 + datetime.timedelta(minutes=delay)
#     print("time1 {}  time2 {}  delay  {}  tdelay    {}".format(time1, time2, delay, tdelay))
#     if time1 > tdelay:
#         print("True tdelay")
#         return True
#     print("False")
#     return False

def checkTimeOfYear():
    date = datetime.date.today()
    if date.month > 4 and date.month < 9:
        return "SUMMER"
    if date.month > 9 and date.month < 4:
        return "WINTER"
    return None

# def getModTempForTime(currentTime, timeModList):
#     """
#     currentTime => datetime object
#     timeModList => [start time, end time, modifier]
#     """
#     time = currentTime.strftime("%H%M")
#     if time >= timeModList[0] and time <= timeModList[1]:
#         return timeModList[2]
#     return 0
