import logging
import urllib.request
import json
import datetime

try:
    import hvactools
except ModuleNotFoundError:
    import thermostat.hvactools as hvactools

class WeatherForecast(hvactools.TimedObject):
    def __init__(self, url, delay=20):
        self.LOGGER = logging.getLogger("__main__.tools.WeatherForecast")
        hvactools.TimedObject.__init__(self, delay)
        self.url = url
        self.__forecast = None

    @property
    def forecast(self):
        return self.__forecast

    @forecast.setter
    def forecast(self, data):
        self.__forecast = data

    def update(self, jsonFile):
        try:
            with urllib.request.urlopen(jsonFile) as url:
                data = json.loads(url.read().decode())
                self.__lastCheck = datetime.datetime.now()
                self.LOGGER.debug("Weather forecast downloaded from darksky")
        except Exception as e:
            self.LOGGER.error("Could not download weather.  Error code {}".format(e))
            data = None
    #         return data
        self.forecast = data
        self.__lastCheck = datetime.datetime.now()
