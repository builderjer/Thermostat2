# Miscelanous tools to help with various processing

import logging
import urllib.request
import json
import pathlib
from pathlib import Path
import datetime

LOGGER = logging.getLogger("__main__.tools")
LOGGER.debug("Loading hvactools")

class TimedObject():
    def __init__(self, delayTime):
        self.delay = delayTime
        self.__lastCheck = None

    @property
    def lastCheck(self):
        return self.__lastCheck

    @lastCheck.setter
    def lastCheck(self, newTime):
        self.__lastCheck = newTime

    def shouldUpdate(self):
        try:
            if datetime.datetime.now() > self.lastCheck + datetime.timedelta(minutes=self.delay):
                return True
            return False
        except TypeError as e:
            if self.lastCheck == None:
                return True
        return False

    def update():
        """
        This function should be overridden in Child class
        """
        pass

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
