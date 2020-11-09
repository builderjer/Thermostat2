import logging
import datetime
import sys
import time

try:
    import sensors
except ModuleNotFoundError:
    import thermostat.sensors as sensors
try:
    import hvactools
except ModuleNotFoundError:
    import thermostat.hvactools as hvactools

from pymata4 import pymata4

class HVAC:
    def __init__(self):
        self.LOGGER = logging.getLogger("__main__.hvac.HVAC")

        self.validStates = ["OFF", "ON"]

        self.__state = "OFF"
        self.__thermostat = None
        self.__heater = None
        self.__vent = None
        self._ac = None

        self.board = None

        self.LOGGER.debug("Created HVAC object")

    @property
    def thermostat(self):
        self.LOGGER.debug("Getting Thermostat")
        return self.__thermostat

    @thermostat.setter
    def thermostat(self, thermostatObject):
        if type(thermostatObject) != type(Thermostat()):
            self.LOGGER.error("{} is not a Thermostat object.  hvac.py class Thermostat".format(thermostatObject))
            self.__thermostat = None
        else:
            self.LOGGER.debug("Setting Thermostat")
            self.__thermostat = thermostatObject

    @property
    def heater(self):
        self.LOGGER.debug("Getting Heater")
        return self.__heater

    @heater.setter
    def heater(self, heaterObject):
        self.LOGGER.debug("Setting Heater")
        self.__heater = heaterObject

    @property
    def vent(self):
        self.LOGGER.debug("Getting vent")
        return self.__vent

    @vent.setter
    def vent(self, ventObject):
        self.LOGGER.debug("Setting vent")
        self.__vent = ventObject

    @property
    def ac(self):
        self.LOGGER.debug("Getting ac")
        return self.__ac

    @ac.setter
    def ac(self, acObject):
        self.LOGGER.debug("Setting ac")
        self.__ac = acObject

    @property
    def state(self):
        self.LOGGER.debug("HVAC state is {}".format(self.__state))
        return self.__state

    @state.setter
    def state(self, newState):
        if newState != self.state:
            self.__state = newState
        else:
            self.__state = self.__state
        self.LOGGER.debug("HVAC state changed to {}".format(newState))

    def turnOn(self, componant):

        if componant.upper() == "HEAT":
            # Give the latching relay power on signal
            self.board.digital_write(self.heater.controlPins[0], 1)
            time.sleep(.25)
            # I am using latching relays, so I will remove the power to it
            self.board.digital_write(self.heater.controlPins[0], 0)
            time.sleep(.25)

            self.heater.state = "ON"

        elif componant.upper() == "COOL":
            self.board.digital_write(self.ac.controlPins[0], 1)
            time.sleep(.25)
            # I am using latching relays, so I will remove the power to it
            self.board.digital_write(self.ac.controlPins[0], 0)
            time.sleep(.25)

            self.ac.state = "ON"

        elif componant.upper() == "VENT":
            self.board.digital_write(self.vent.controlPins[0], 1)
            time.sleep(.25)
            self.board.digital_write(self.vent.controlPins[0], 0)
            time.sleep(1)

            self.vent.state = "ON"

        else:
            self.LOGGER.error("Cannot turn on {}. Not a valid object".format(componant))
            return

        self.LOGGER.info("Turned {} on".format(componant))
        return True

    def turnOff(self, componant):

        if componant.upper() == "ALL":
            self.board.digital_write(self.heater.controlPins[1], 1)
            time.sleep(.25)
            # I am using latching relays, so I will remove the power to it
            self.board.digital_write(self.heater.controlPins[1], 0)
            time.sleep(.25)

            self.heater.state = "OFF"

            self.board.digital_write(self.ac.controlPins[1], 1)
            # self.board.digital_write(self.vent.controlPin[1], 1)
            time.sleep(.25)
            # I am using latching relays, so I will remove the power to it
            self.board.digital_write(self.ac.controlPins[1], 0)
            time.sleep(.25)

            self.ac.state = "OFF"

            self.board.digital_write(self.vent.controlPins[1], 1)
            time.sleep(.25)
            self.board.digital_write(self.vent.controlPins[1], 0)
            time.sleep(1)
            self.LOGGER.debug("Vent state turned off")

            self.vent.state = "OFF"

        elif componant.upper() == "HEAT":
            self.board.digital_write(self.heater.controlPins[1], 1)
            time.sleep(.25)
            # I am using latching relays, so I will remove the power to it
            self.board.digital_write(self.heater.controlPins[1], 0)
            time.sleep(.25)

            self.heater.state = "OFF"

        elif componant.upper() == "COOL":
            self.board.digital_write(self.ac.controlPins[1], 1)
            # self.board.digital_write(self.vent.controlPin[1], 1)
            time.sleep(.25)
            # I am using latching relays, so I will remove the power to it
            self.board.digital_write(self.ac.controlPins[1], 0)
            time.sleep(.25)

            self.ac.state = "OFF"

        elif componant.upper() == "VENT":
            self.board.digital_write(self.vent.controlPins[1], 1)
            time.sleep(.25)
            self.board.digital_write(self.vent.controlPins[1], 0)
            time.sleep(1)
            self.LOGGER.debug("Vent state turned off")

            self.vent.state = "OFF"

        else:
            self.LOGGER.error("Cannot turn off {}. Not a valid object".format(componant))
            return

        self.LOGGER.info("Turned {} off".format(componant))
        return True

class Thermostat(hvactools.TimedObject):
    def __init__(self, delay=720):
        self.LOGGER = logging.getLogger("__main__.hvac.Thermostat")
        hvactools.TimedObject.__init__(self, delay)
        self.validFormats = ["F", "C"]
        self.validModes = ["AUTO", "MANUAL"]
        self.validStates = ["OFF", "HEAT", "COOL", "VENT"]

        self.__tempFormat = "F"
        self.__mode = "AUTO"
        self.__state = "OFF"

        self.tempSensors = []
        self.sensorGroups = {}

        self.__defaultTemp = None
        self.__desiredTemp = None
        self.__tempModifier = 0
        self.__minTemp = 65
        self.__maxTemp = 78

        self.LOGGER.debug("Created Thermostat object")

    @property
    def tempFormat(self):
        self.LOGGER.debug("Getting temp format")
        return self.__tempFormat

    @tempFormat.setter
    def tempFormat(self, tFormat):
        self.LOGGER.debug("Setting temp format")
        if tFormat in self.validFormats:
            self.__tempFormat = tFormat
        else:
            self.__tempFormat = self.__tempFormat

    @property
    def mode(self):
        self.LOGGER.debug("Getting thermostat mode")
        # print("getting thermostat mode")
        return self.__mode

    @mode.setter
    def mode(self, tMode):
        self.LOGGER.debug("Setting thermostat mode")
        # print("setting thermostat mode")
        if tMode in self.validModes and tMode != self.mode:
            self.__mode = tMode
        else:
            self.LOGGER.error("{} is not a valid mode for Thermostat.mode".format(tMode))
            self.__mode = self.__mode

    @property
    def state(self):
        self.LOGGER.debug("Thermostat state is {}".format(self.__state))
        return self.__state

    @state.setter
    def state(self, newState):
        if newState in self.validStates and newState != self.state:
            self.LOGGER.debug("Setting state to {}".format(newState))
            self.__state = newState
        else:
            self.__state = self.__state

    @property
    def minTemp(self):
        self.LOGGER.debug("Getting minimum temp")
        return self.__minTemp

    @minTemp.setter
    def minTemp(self, temp):
        self.LOGGER.debug("Setting minimum temp to {}".format(temp))
        self.__minTemp = temp

    @property
    def maxTemp(self):
        self.LOGGER.debug("Getting maximum temp")
        return self.__maxTemp

    @maxTemp.setter
    def maxTemp(self, temp):
        self.LOGGER.debug("Setting the maximum temp to {}".format(temp))
        self.__maxTemp = temp

    @property
    def defaultTemp(self):
        self.LOGGER.debug("Getting default temp setting")
        return __defaultTemp

    @defaultTemp.setter
    def defaultTemp(self, temp):
        self.LOGGER.debug("Setting default temp")
        self.__defaultTemp = temp

    @property
    def desiredTemp(self):
        self.LOGGER.debug("Getting desired temp of {}".format(self.__desiredTemp))
        return self.__desiredTemp

    @desiredTemp.setter
    def desiredTemp(self, dTemp):
        self.LOGGER.debug("Setting desired temp to {}".format(dTemp))
        if dTemp <= self.maxTemp and dTemp >= self.minTemp:
            self.__desiredTemp = dTemp
        if dTemp > self.maxTemp:
            self.LOGGER.error("{} is higher than the max temp of {}".format(dTemp, self.maxTemp))
            self.__desiredTemp = self.maxTemp
        if dTemp < self.minTemp:
            self.LOGGER.error("{} is lower than the min temp of {}".format(dTemp, self.minTemp))
            self.__desiredTemp = self.minTemp

    @property
    def tempModifier(self):
        return self.__tempModifier

    @tempModifier.setter
    def tempModifier(self, modDict):
        mod = 0
        for modifier, value in modDict.items():
            if modifier == "TIMEMODS":
                now = datetime.datetime.now().strftime("%H%M")
                for time in modDict[modifier].values():
                    if now >= time[0] and now <= time[1]:
                        mod += time[2]
            if modifier == "OCCUPIED":
                if modDict[modifier][0]:
                    mod += modDict[modifier][1]["HOME"][2]
                else:
                    mod += modDict[modifier][1]["AWAY"][2]
        self.LOGGER.debug("temp mod is {}".format(mod))
        self.__tempModifier = mod

    def addSensor(self, sensor):
        if sensor not in self.tempSensors:
            self.LOGGER.debug("Adding {} to tempSensors".format(sensor))
            self.tempSensors.append(sensor)
        else:
            self.LOGGER.error("tempSensors already contains {}".format(sensor))

    def createSensorGroup(self, groupName):
        if groupName not in self.sensorGroups:

        # for name in groupNames:
        #     if name not in self.sensorGroups:
            self.LOGGER.debug("Created sensor group {}".format(groupName))
            self.sensorGroups[groupName] = []
        else:
            self.LOGGER.error("{} is already a sensor group".format(groupName))

    def addSensorToGroup(self, sensor, group):
        if group in self.sensorGroups:
            if sensor not in self.sensorGroups[group]:
                self.LOGGER.debug("Adding sensor {} to group {}".format(sensor.name, group))
                self.sensorGroups[group].append(sensor)
            else:
                self.LOGGER.error("Sensor {} is already part of the group {}".format(sensor, group))
        else:
            self.LOGGER.error("The group {} does not exist")

    def updateSensors(self, board):
        for tSensor in self.tempSensors:
            r = 10
            tempArray = []
            # tSum = 0
            self.LOGGER.debug("Updating sensor {}".format(tSensor.name))
            for reading in range(r):
                value, timeStamp = board.analog_read(tSensor.controlPin)
                self.LOGGER.debug(value)
                if value:
                    tempArray.append(value)
                # tSum += value
                time.sleep(.1)
            try:
                average = sum(tempArray) / len(tempArray)
            # average = tSum / r
                if 30 < average < 60:
                    tSensor.tempC = average
                else:
                    if tSensor.tempC:
                        tSensor.tempC = tSensor.tempC
                    # else:
                    #     tSensor.tempC = (self.desiredTemp - 32) * (5/9)

                        # (32°F − 32) × 5/9 = 0°C
            except ZeroDivisionError as e:
                self.LOGGER.error("Sensor {} is having an error".format(tSensor.name))
                # BIG hack to maybe help a None result?
                tSensor.tempC = (self.desiredTemp - 32) * (5/9)

    def getTemp(self, area):
        for tSensor in self.tempSensors:
            if area.upper() == tSensor.name:
                if self.tempFormat == "F":
                    return self.tempF
                else:
                    return self.tempC
        self.LOGGER.debug("{} not a name of specific sensor.  Trying group names".format(area))
        for group in self.sensorGroups:
            if area.upper() == group:
                tempArray = []
                for tempSensor in self.sensorGroups[group]:

                # tSum = 0
                # for tSensor in self.sensorGroups[group]:
                    if self.tempFormat == "F":
                        if tempSensor.tempF:
                            tempArray.append(tempSensor.tempF)
                    else:
                        if tempSensor.tempC:
                            tempArray.append(tempSensor.tempC)
                return (sum(tempArray) / len(tempArray))
                #         tSum += tSensor.tempF
                #     else:
                #         tSum += tSensor.tempC
                # return (tSum / len(self.sensorGroups[group]))
        self.LOGGER.debug("{} is not in the grouped sensors either.  Skipping".format(area))

    def update(self, conditionList):
        highTemp, lowTemp, timeOfYear = conditionList
        # Reset the delay if different than the default delay
        if self.delay != self.defaultDelay:
            self.delay = self.defaultDelay

        # Reset to AUTO mode if updating from MANUAL
        if self.mode == "MANUAL":
            self.mode = "AUTO"
            
        if not timeOfYear:
            if highTemp > self.maxTemp + 10 and lowTemp < self.minTemp - 20:
                self.LOGGER.debug("You must live in Colorado")
                if highTemp > self.maxTemp + 10:
                    self.state = "COOL"
                elif lowTemp < self.minTemp - 20:
                    self.state = "HEAT"

            elif highTemp > self.maxTemp + 5:
                self.LOGGER.debug("Gonna be hot. Set state to COOL")
                self.state = "COOL"

            elif lowTemp < self.minTemp - 15:
                self.LOGGER.debug("Gonna be cold. Set state to HEAT")
                self.state = "HEAT"

            # BUG: Another hack to make this work if there is no weather
            elif highTemp == self.maxTemp and lowTemp == self.minTemp:
                self.LOGGER.debug("no weather")
                # Day time
                now = datetime.datetime.now()
                if now.month == 10:
                    self.state = "HEAT"
                else:
                    self.state = "COOL"
                # if now.hour >=7 and now.hour <= 19:
                #     self.state = "COOL"
                # else:
                #     self.state = "HEAT"

        elif timeOfYear == "SUMMER":
            self.state = "COOL"

        elif timeOfYear == "WINTER":
            self.state = "HEAT"

        # BUG: Another hack to make this work if there is no weather
        elif highTemp == self.maxTemp and lowTemp == self.minTemp:
            self.LOGGER.debug("no weather again")
            # Day time
            now = datetime.datetime.now()
            if now.hour >=7 and now.hour <= 19:
                self.state = "COOL"
            else:
                self.state = "HEAT"

        else:
            self.state = "OFF"

        self.lastCheck = datetime.datetime.now()

class Heater(hvactools.TimedObject):
    def __init__(self, delay=2):
        self.LOGGER = logging.getLogger("__main__.hvac.Heater")
        hvactools.TimedObject.__init__(self, delay)
        self.__controlPins = None
        self.validStates = ["ON", "OFF"]
        self.__state = "OFF"

        self.LOGGER.debug("Created Heater object")

    @property
    def controlPins(self):
        self.LOGGER.debug("Getting heater controlPins")
        return self.__controlPins

    @controlPins.setter
    def controlPins(self, pins):
        self.LOGGER.debug("Setting heater controlPins {}".format(pins))
        if len(pins) != 2:
            self.LOGGER.error("There must be exactly 2 pins defined.  (onPin, offPin)")
            self.__controlPins = self.__controlPins
        else:
            self.__controlPins = (pins[0], pins[1])

    @property
    def state(self):
        self.LOGGER.debug("Getting heater state of {}".format(self.__state))
        return self.__state

    @state.setter
    def state(self, onOff):
        if onOff in self.validStates:
            self.__state = onOff
            self.LOGGER.debug("Set Heater to state {}".format(self.state))
        else:
            self.LOGGER.error("{} is not a valid state for heater".format(onOff))
            self.__state = self.__state
        self.LOGGER.debug("Set heater state to {}".format(self.state))

    def update(self):
        self.LOGGER.debug("Updating Heater")
        self.lastCheck = datetime.datetime.now()

class Vent(hvactools.TimedObject):
    def __init__(self, delay=2):
        self.LOGGER = logging.getLogger("__main__.hvac.Vent")
        hvactools.TimedObject.__init__(self, delay)
        self.__controlPins = None
        self.validStates = ["ON", "OFF"]
        self.__state = "OFF"

        self.LOGGER.debug("Created Vent object")

    @property
    def controlPins(self):
        self.LOGGER.debug("Getting vent controlPins")
        return self.__controlPins

    @controlPins.setter
    def controlPins(self, pins):
        self.LOGGER.debug("Setting vent controlPins {}".format(pins))
        if len(pins) != 2:
            self.LOGGER.error("There must be exactly 2 pins defined.  (onPin, offPin)")
            self.__controlPins = self.__controlPins
        else:
            self.__controlPins = (pins[0], pins[1])

    @property
    def state(self):
        self.LOGGER.debug("Getting vent state")
        return self.__state

    @state.setter
    def state(self, onOff):
        self.LOGGER.debug("Setting vent state")
        if onOff in self.validStates:
            self.__state = onOff
        else:
            self.LOGGER.error("{} is not a valid state for vent".format(onOff))
            self.__state = self.__state
    def update(self):
        self.lastCheck = datetime.datetime.now()

class AirConditioner(hvactools.TimedObject):
    def __init__(self, delay=2):
        self.LOGGER = logging.getLogger("__main__.hvac.AirConditioner")
        hvactools.TimedObject.__init__(self, delay)
        self.__controlPins = None
        self.validStates = ["ON", "OFF"]
        self.__state = "OFF"

        self.LOGGER.debug("Created AirConditioner object")

    @property
    def controlPins(self):
        self.LOGGER.debug("Getting ac controlPins")
        return self.__controlPins

    @controlPins.setter
    def controlPins(self, pins):
        self.LOGGER.debug("Setting ac controlPins {}".format(pins))
        if len(pins) != 2:
            self.LOGGER.error("There must be exactly 2 pins defined.  (onPin, offPin)")
            self.__controlPins = self.__controlPins
        else:
            self.__controlPins = (pins[0], pins[1])

    @property
    def state(self):
        self.LOGGER.debug("Getting ac state")
        return self.__state

    @state.setter
    def state(self, onOff):
        self.LOGGER.debug("Setting ac state")
        if onOff in self.validStates:
            self.__state = onOff
        else:
            self.LOGGER.error("{} is not a valid state for ac".format(onOff))
            self.__state = self.__state

    def update(self):
        self.lastCheck = datetime.datetime.now()

def setup(tempSensors, sensorGroups, hvacControlPins):
    LOGGER = logging.getLogger("__main__.hvac.setup")
    LOGGER.debug("tempSensors {}\nsensorGroups {}\nhvacControlPins {}".format(tempSensors, sensorGroups, hvacControlPins))
    hvac = HVAC()
    # Setup the thermostat
    hvac.thermostat = Thermostat()
    # Add the sensors to the thermostat
    for sensorName, sensorData in tempSensors.items():
        hvac.thermostat.addSensor(sensors.TempSensor(sensorName, sensorData[0], sensorData[1]))
    # Create the groups of sensors
    for groupName, sensorNames in sensorGroups.items():
        hvac.thermostat.createSensorGroup(groupName)
        # Add the sensors to the group
        for sName in sensorNames:
            for sensor in hvac.thermostat.tempSensors:
                if sName == sensor.name:
                    hvac.thermostat.addSensorToGroup(sensor, groupName)
    # Setup the heater
    hvac.heater = Heater()
    hvac.heater.controlPins = hvacControlPins["HEAT_PINS"]

    # Setup the vent
    hvac.vent = Vent()
    hvac.vent.controlPins = hvacControlPins["VENT_PINS"]

    # Setup the AC
    hvac.ac = AirConditioner()
    hvac.ac.controlPins = hvacControlPins["AC_PINS"]

    # Setup the pymata board
    hvac.board = pymata4.Pymata4()

    # Add all of the control and sensor pins to the board
    # Sensor pins
    for tSensor in hvac.thermostat.tempSensors:
        hvac.board.set_pin_mode_analog_input(tSensor.controlPin)
        # LOGGER.debug("{}  {}".format(tSensor, tSensor.controlPin))
    # Control pins
    # Heater
    for pin in hvac.heater.controlPins:
        hvac.board.set_pin_mode_digital_output(pin)
        LOGGER.debug("heater controlPin  {}".format(pin))
    # Vent
    for pin in hvac.vent.controlPins:
        hvac.board.set_pin_mode_digital_output(pin)
        LOGGER.debug("vent controlPin  {}".format(pin))
    # AC
    for pin in hvac.ac.controlPins:
        hvac.board.set_pin_mode_digital_output(pin)
        LOGGER.debug("ac controlPin  {}".format(pin))

    return hvac
