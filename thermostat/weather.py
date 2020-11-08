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
        self.__messages = []

    @property
    def messages(self):
        return self.__messages

    @messages.setter
    def messages(self, data):
        self.__messages = [
        	# Current readings
        	{
        		"topic": "ziggy/weather/current/summary",
        		"payload": data["currently"]["summary"],
        		"qos": 1,
        		"retain": True
        		},
        	{
        		"topic": "ziggy/weather/current/icon",
        		"payload": data["currently"]["icon"],
        		"qos": 1,
        		"retain": True
        		},
        	{
        		"topic": "ziggy/weather/current/temp",
        		"payload": data["currently"]["temperature"],
        		"qos": 1,
        		"retain": True
        		},

        	# Daily forecast
        	{
        		"topic": "ziggy/weather/daily/summary",
        		"payload": data["daily"]["data"][0]["summary"],
        		"qos": 1,
        		"retain": True
        		},
        	{
        		"topic": "ziggy/weather/daily/icon",
        		"payload": data["daily"]["data"][0]["icon"],
        		"qos": 1,
        		"retain": True
        		},
        	{
        		"topic": "ziggy/weather/daily/tempHigh",
        		"payload": data["daily"]["data"][0]["temperatureHigh"],
        		"qos": 1,
        		"retain": True
        		},
        	{
        		"topic": "ziggy/weather/daily/tempLow",
        		"payload": data["daily"]["data"][0]["temperatureLow"],
        		"qos": 1,
        		"retain": True
        		},

        	# Weekly summary
        	{
        		"topic": "ziggy/weather/weekly/summary",
        		"payload": data["daily"]["summary"],
        		"qos": 1,
        		"retain": True
        	}
        ]
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
                self.LOGGER.debug("Weather forecast downloaded from darksky")
                self.forecast = data
                self.lastCheck = datetime.datetime.now()
        except Exception as e:
            self.LOGGER.error("Could not download weather.  Error code {}".format(e))
            data = None
    #         return data
