"""
This script is to hold a variety of sensors used in my personal smarthome.
https://github.com/builderjer/ZiggyAI
"""

__author__ = "builderjer"
__version__ = "0.1.4"

import logging
import subprocess
import sys

LOGGER = logging.getLogger("__main__.sensors.py")

class Sensor:
	"""
	Base class for all sensors in this file.
	"""
	def __init__(self, name):
		"""
		name => Must be initiated with a name.
		"""
		self.LOGGER = logging.getLogger("__main__.sensors.Sensor")
		self._name = name.upper()

	@property
	def name(self):
		return self._name

	@name.setter
	def name(self, name):
		self._name = name.upper()

class TempSensor(Sensor):
#class TempSensor:
	"""
	A class to create a temperature sensor for use with an Arduino or other microcontroller
	"""
	def __init__(self, name, moduleType, controlPin):
		"""
		<string> moduleType => type of sensor (LM35, etc...)
			It is required because each sensor uses a different forumla to determine the temp

		<int> controlPin => The pin on the microcontroller the sensor is connected to.
		"""
		self.LOGGER = logging.getLogger("__main__.sensors.TempSensor")
		self.LOGGER.debug("Created TempSensor {} with moduleType {} and controlPin {}".format(name, moduleType, controlPin))

		super().__init__(name)

		self._moduleType = moduleType.upper()

		if type(controlPin) == int:
			self._controlPin = controlPin
		else:
			try:
				self._controlPin = int(controlPin)
			except ValueError as e:
				self.LOGGER.error("Sensor {} was setup with an invalid controlPin.\n	{} must be an intiger".format(self.name, controlPin))
				self._controlPin = None

		self._tempC = None
		self._tempF = None

	# Purposly no setter for this property.  It can not be changed.
	@property
	def moduleType(self):
		return self._moduleType

	@property
	def controlPin(self):
		return self._controlPin

	@controlPin.setter
	def controlPin(self, pinNumber):
		self.LOGGER.debug("Setting controlPin number {}".format(pinNumber))
		self._controlPin = pinNumber

	@property
	def tempC(self):
		return self._tempC

	@tempC.setter
	def tempC(self, rawValue):
		"""
		rawValue => The raw sensor value before any conversions
		"""
		self.LOGGER.debug("Setting tempC with rawValue {}".format(rawValue))
		# Do all of the conversions here.  It uses the moduleType to determine what conversion to use.
		try:
			if self.moduleType == "LM35":
				self._tempC = rawValue * 0.48828125
				# # Convert to Fahernheit while we are at it
				# self._tempF = self._tempC
			else:
				self._tempC = None
		except TypeError as e:
			self.LOGGER.debug("error is here {}".format(e))
			self._tempC = self._tempC

	# Most sensors use Centigrade, but this converts it to Fahernheit
	@property
	def tempF(self):
		# LM35 uses centigrade as its base temp.  Use that for the conversion
		if self.tempC:
			tF = (self.tempC * 1.8) + 32
			self.LOGGER.debug("tempC: {}  tempF: {}".format(self.tempC, tF))
			return tF
		else:
			self.LOGGER.error("No tempC to convert sensor {}".format(self.name))
			return None

class PresenceDetector:
	"""
	A Class to try and determine if there is anybody in the house.  For now,
		it only uses a simple wifi ping.

	Must have static IP addresses assigned to the phones or devices used.
	Must have the setting for the IP address also
	"""
	def __init__(self):
		self.LOGGER = logging.getLogger("__main__.sensors.PresenceDetector")
		self.addresses = {}
		self._homeList = []

	@property
	def homeList(self):
		return self._homeList

	@homeList.setter
	def homeList(self, addressList):
		tempList = []
		for name in self.addresses:
			try:
				# NOTE: This only works on Linux...For now
				if subprocess.check_output(["ping", "-c", "1", self.addresses[name]]):
					tempList.append(name)
			except subprocess.CalledProcessError as e:
				self.LOGGER.info("{} at {} not reachable".format(name, self.addresses[name]))
		self._homeList = tempList

	def addAddress(self, name, address):
		if name not in self.addresses:
			self.addresses[name] = address

	def removeAddress(self, name):
		if name in self.addresses:
			del self.addresses[name]

class WiFiDetector(Sensor):
	def __init__(self):
		self.LOGGER = logging.getLogger("__main__.sensors.WiFiDetector")

		self.__addresses = {}

	@property
	def addresses(self):
		return self.__addresses

	def addAddress(self, name, address):
		if name not in self.addresses:
			self.__addresses[name] = address
			self.LOGGER.debug("Added {} with address of {} to address list".format(name, address))
		else:
			if address not in self.addresses[name]:
				self.__addresses[name].append(address)
				self.LOGGER.debug("Added the address {} to an existing {}".format(address, name))

	def removeAddress(self, name, address):
		if name not in self.addresses:
			self.LOGGER.error("There is no {} in the address list".format(name))
			return False
		if address not in self.addresses[name]:
			self.LOGGER.error("There is no address {} for {}".format(address, name))
			return False
		self.addresses[name].remove(address)
		self.LOGGER.debug("Removed address {} from {}".format(address, name))

	def pingAddress(self, address):
		if sys.platform == "linux":
			try:
				subprocess.check_output(["ping", "-c", "1", address])
				return True
			except subprocess.CalledProcessError as e:
				self.LOGGER.error("{} unreachable".format(address))
				return False
		else:
			# do other os here
			self.LOGGER.error("{} is not yes supported. Please create a pull request".format(sys.platform))
			return False


#class PhotoSensor:
	#"""
	#A photo resistor sensing the amount of light in a given area.
	#"""
	#def __init__(self, controlPin):
		#self.controlPin = controlPin
