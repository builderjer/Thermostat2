import logging
import datetime
import subprocess

try:
    import constants
except ModuleNotFoundError:
    import thermostat.constants as constants
try:
    import hvactools
except ModuleNotFoundError:
    import thermostat.hvactools as hvactools

LOGGER = logging.getLogger("__main__.occupancy")

domainName = constants.DOMAINNAME

class Occupancy():
    def __init__(self):
        self.LOGGER = logging.getLogger("__main__.occupancy.Occupancy")
        self.__occupied = "AWAY"

    @property
    def occupied(self):
        LOGGER.debug("Getting Occupied")
        if self.__occupied == "HOME":
            return True
        return False

    @occupied.setter
    def occupied(self, trueFalse):
        LOGGER.debug("Setting Occupied to {}".format(trueFalse))
        if trueFalse:
            self.__occupied = "HOME"
        else:
            self.__occupied = "AWAY"

class WiFi(Occupancy, hvactools.TimedObject):
    """docstring for WiFi."""

    def __init__(self, peopleDict, delay=15):
        self.LOGGER = logging.getLogger("__main__.occupancy.WiFi")
        hvactools.TimedObject.__init__(self, delay)
        Occupancy().__init__()
        # self.delay = delay
        self.peopleDict = peopleDict
        # self.__lastCheck = None
        self.__home = None

        self.LOGGER.debug("Created WiFi object")

    # @property
    # def lastCheck(self):
    #     return self.__lastCheck
    #
    # @lastCheck.setter
    # def lastCheck(self, checkTime):
    #     self.__lastCheck = checkTime

    @property
    def home(self):
        return self.__home

    @home.setter
    def home(self, people):
        tempList = []
        for person, hostnames in people.items():
            for hName in hostnames:
                try:
                    if subprocess.check_output(["ping", "-c", "1", hName + domainName]):
                        if person not in tempList:
                            tempList.append(person)
                except subprocess.CalledProcessError as e:
                    self.LOGGER.error("{} at {} not reachable".format(person, hName + domainName))
        if tempList:
            self.__home = tempList
        else:
            self.__home = None
        self.LOGGER.debug(self.__home)
        self.__lastCheck = datetime.datetime.now()

    def update(self, wifiAddresses):
        if wifiAddresses:
            self.home = wifiAddresses
        if self.home:
            self.occupied = True
        else:
            self.occupied = False
        self.lastCheck = datetime.datetime.now()
