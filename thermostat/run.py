#!/usr/bin/env python3

import sys
import json
from pathlib import Path
import datetime
import time
import logging
from logging.config import fileConfig

from pymata4 import pymata4

# Local imports
import constants
import hvactools
import hvac
import sensors
import weather
import occupancy

# TODO: more logging configuration
# Setup a logger
fileConfig(constants.LOGGERCONFIG)
LOGGER = logging.getLogger(__name__)

# Check to make sure we are runing python 3.7 or greater"
if sys.version_info.major < 3 or sys.version_info.minor < 7:
	LOGGER.error("You need to be running python 3.7 or later")
	sys.exit()

SETTINGS = hvactools.updateSettings(None, constants.DEFAULTCONFIG)
# SETTINGS = hvactools.loadSettings(constants.DEFAULTCONFIG)
if not SETTINGS:
	LOGGER.error("Settings file did not load. Check the configuration and try again")
	sys.exit()
else:
	LOGGER.info("Default settings loaded")

# Check for user settings
uSettings = Path(Path.home(), constants.USERCONFIG)
if uSettings.exists():
	SETTINGS = hvactools.updateSettings(SETTINGS, uSettings)
else:
	# Try and create a user config file to be used later
	try:
		Path.mkdir(uSettings.parent, parents=True, exist_ok=True)
		with open(uSettings, "w") as uConfig:
			json.dump(SETTINGS, uConfig, indent=4)
	except Exception as e:
		LOGGER.error("Could not create user config file {}.   {}".format(uSettings, e))

# Setup the HVAC system
HVAC = hvac.setup(SETTINGS["SENSORS"], SETTINGS["SENSOR_GROUPS"], SETTINGS["HVAC"])
# Setup the weather forecast system
WEATHER = weather.WeatherForecast(SETTINGS["WEATHER"]["URL"])
# Setup the WiFi ooccupancy detector
WIFI = occupancy.WiFi(SETTINGS["WIFI"])

# Give the thermostat a default temp to work with
HVAC.thermostat.defaultTemp = SETTINGS["TEMP_SETTINGS"]["DEFAULT_TEMP"]
HVAC.turnOff("ALL")
while True:
	####################################################
	# This happens when the thermostat is in AUTO mode
	####################################################
	while HVAC.thermostat.mode == "AUTO":
		# Update the sensors
		HVAC.thermostat.updateSensors(HVAC.board)
		# Since this hvac supplies the house, the HOUSE group is the default
		# group that the thermostat will monitor
		houseTemp = round(HVAC.thermostat.getTemp("HOUSE"))
		LOGGER.debug("House temp is {}".format(houseTemp))

		# Check the weather every "delay" minutes
		# We need the weather to set the state of the thermostat
		if WEATHER.shouldUpdate():
			print("Weather needs a break")
			# WEATHER.update(WEATHER.url)
		# Set the state of the thermostat every "delay" minutes default => 1440 (one day)
		if HVAC.thermostat.shouldUpdate():
			try:
				HVAC.thermostat.update((WEATHER.forecast["daily"]["data"][0]["temperatureHigh"], WEATHER.forecast["daily"]["data"][0]["temperatureLow"], hvactools.checkTimeOfYear()))
			except TypeError as e:
				LOGGER.error("Error updating thermostat  {}".format(e))
				 # BUG:  Hack for if the weather fails
				HVAC.thermostat.update((HVAC.thermostat.maxTemp, HVAC.thermostat.minTemp, hvactools.checkTimeOfYear()))

		# See if there is anybody home
		# Only check every so often => WIFI.delay
		if WIFI.shouldUpdate():
			WIFI.update(SETTINGS["WIFI"])

		# Set the desired temperature of the house
		if HVAC.thermostat.state != "OFF":
			HVAC.thermostat.tempModifier = {"TIMEMODS": SETTINGS["TEMP_SETTINGS"][HVAC.thermostat.state]["TIME_SETTINGS"], "OCCUPIED": [WIFI.occupied, SETTINGS["TEMP_SETTINGS"][HVAC.thermostat.state]["OCCUPIED_SETTINGS"]]}
			HVAC.thermostat.desiredTemp = SETTINGS["TEMP_SETTINGS"][HVAC.thermostat.state]["DEFAULT_TEMP"] + HVAC.thermostat.tempModifier
		else:
			HVAC.thermostat.desiredTemp = SETTINGS["TEMP_SETTINGS"]["DEFAULT_TEMP"]

		# Check if the HVAC should turn on or off
		# House is hot
		if houseTemp > HVAC.thermostat.desiredTemp:
			LOGGER.debug("House is HOT")

			if HVAC.thermostat.state == "HEAT" and HVAC.heater.state == "ON":
				LOGGER.debug("Heater is on")
				# I put the heater/vent/ac on a timer so it does not go on and off
				# if there is a glitch in the temp sensors
				if HVAC.heater.shouldUpdate():
					LOGGER.debug("Been on for a while")
					HVAC.heater.update()

					HVAC.turnOff("HEAT")

			elif HVAC.thermostat.state == "COOL" and HVAC.ac.state == "OFF":
				HVAC.turnOn("COOL")

			else:
				LOGGER.debug("House is hot, but to early to update, so, WE GOOD")
		# House is cold
		elif houseTemp < HVAC.thermostat.desiredTemp:
			LOGGER.debug("House is cold")
			if HVAC.thermostat.state == "HEAT" and HVAC.heater.state == "OFF": # and HVAC.heater.shouldUpdate():
				# HVAC.heater.update()
				LOGGER.debug("Heater is off")
				if HVAC.heater.shouldUpdate():
					LOGGER.debug("been off for a while")
					HVAC.heater.update()

					HVAC.turnOn("HEAT")

			elif HVAC.thermostat.state == "COOL" and HVAC.ac.state == "ON":
				HVAC.turnOff("COOL")

			else:
				LOGGER.debug("House is cold, but too early to update, so, WE GOOD IN CHILL")

		else:
			LOGGER.debug("House temp is the same. Heater state is {}".format(HVAC.heater.state))
		time.sleep(1)

	while HVAC.thermostat.mode == "MANUAL":
		HVAC.turnOff("ALL")
