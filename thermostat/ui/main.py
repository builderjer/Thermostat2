from flask import Flask, render_template
from flask_mqtt import Mqtt

# import thermostat.hvac as hvac
# import thermostat.weather as weather
# import thermostat.hvactools as hvactools
# import thermostat.constants as constants
# import thermostat.occupancy as occupancy

app = Flask(__name__)
mqtt = Mqtt(app)

# SETTINGS = hvactools.updateSettings(None, constants.DEFAULTCONFIG)
#
# HVAC = hvac.setup(SETTINGS["SENSORS"], SETTINGS["SENSOR_GROUPS"], SETTINGS["HVAC"])
# WIFI = occupancy.WiFi(SETTINGS["WIFI"])
# WIFI.update(SETTINGS["WIFI"])
#
# WEATHER = weather.WeatherForecast(SETTINGS["WEATHER"]["URL"])
# WEATHER.update(WEATHER.url)
#
# HVAC.thermostat.defaultTemp = SETTINGS["TEMP_SETTINGS"]["DEFAULT_TEMP"]
#
# HVAC.thermostat.updateSensors(HVAC.board)
# # Since this hvac supplies the house, the HOUSE group is the default
# # group that the thermostat will monitor
# houseTemp = round(HVAC.thermostat.getTemp("HOUSE"))
#
# HVAC.thermostat.update((WEATHER.forecast["daily"]["data"][0]["temperatureHigh"], WEATHER.forecast["daily"]["data"][0]["temperatureLow"], hvactools.checkTimeOfYear()))
#
# HVAC.thermostat.tempModifier = {"TIMEMODS": SETTINGS["TEMP_SETTINGS"][HVAC.thermostat.state]["TIME_SETTINGS"], "OCCUPIED": [WIFI.occupied, SETTINGS["TEMP_SETTINGS"][HVAC.thermostat.state]["OCCUPIED_SETTINGS"]]}
# HVAC.thermostat.desiredTemp = SETTINGS["TEMP_SETTINGS"][HVAC.thermostat.state]["DEFAULT_TEMP"] + HVAC.thermostat.tempModifier
#
# cTemp = WEATHER.forecast["currently"]["temperature"]
data = {}
@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    mqtt.subscribe("ziggy/#")

@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    data[message.topic] = message.payload.decode()
    #  = dict(
    #     topic = message.topic,
    #     payload = message.payload.decode()
    # )

@mqtt.on_publish()
def handle_mqtt_publish(client, userdata, mid):
    print("published {}".format(mid))
    
@app.route('/')
def index():
    # return render_template("index.html", hTemp=data["ziggy/climate/temp/house"])
    return render_template("index.html", data=data)
