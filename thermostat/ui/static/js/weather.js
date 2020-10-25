// This script controls the mqtt client and subscribes to several aspects
// of the weather.
// It pulls it's information from DarkSky API

var __author__ = "builderjer"
var __version__ = "0.1.0"

var mqtt;
var reconnectTimeout = 2000;
var host="ziggyhome.mooo.com" ;
var port=8183;

var weatherIconDir = "../assets/images/weather/icon-set/GIF/50x50/";

var currentSummary = "ziggy/weather/current/summary";
var currentIcon = "ziggy/weather/current/icon";
var currentTemp = "ziggy/weather/current/temp";
var dailySummary = "ziggy/weather/daily/summary";
var dailyIcon = "ziggy/weather/daily/icon";
var tempHigh = "ziggy/weather/daily/tempHigh";
var tempLow = "ziggy/weather/daily/tempLow";
var weeklySummary = "ziggy/weather/weekly/summary";

var weather = "ziggy/weather/#";

var tempSensors = "ziggy/house/climate/temp";

// called when the client connects
function onConnect() {
	// Once a connection has been made, make a subscription and send a message.
// 	console.log("onConnect");
	mqtt.subscribe(weather, {"qos": 1});
	mqtt.subscribe(tempSensors + "/#", {"qos": 1});
	
// 	mqtt.subscribe(temp, {"qos":1});
// 	mqtt.subscribe(tempHigh, {"qos":1});
// 	mqtt.subscribe(tempLow, {"qos":1});
// 	mqtt.subscribe(icon, {"qos":1});
// 	mqtt.subscribe(sunrise, {"qos":1});
// 	mqtt.subscribe(sunset, {"qos":1});
// 	mqtt.subscribe(currentTime, {"qos":1});	
}


// called when the client loses its connection
function onConnectionLost(responseObject) {
	if (responseObject.errorCode !== 0) {
		console.log("onConnectionLost:"+responseObject.errorMessage);
	}
}

// called when a message arrives
function onMessageArrived(message) {
	console.log(message.destinationName+"  :  "+message.payloadString);
	
	// Current Readings
	if (message.destinationName == currentSummary) {
		document.getElementById("currentSummary").innerHTML = message.payloadString;
	}
	
	if (message.destinationName == currentIcon) {
		try {
			document.getElementById("currentIcon").src=weatherIconDir+message.payloadString+".gif";
			console.log("in icon try");
		}
		catch(err) {
			document.getElementById("currentIcon").src=weatherIconDir+"na.gif";
			console.log(message.payloadString);
		}
	}
	if (message.destinationName == currentTemp) {
		document.getElementById("currentTemp").innerHTML = Math.round(Number(message.payloadString))+"&deg F";
	}
	
	// Daily forecast
	if (message.destinationName == dailySummary) {
		document.getElementById("dailySummary").innerHTML = message.payloadString;
	}
	if (message.destinationName == dailyIcon) {
		try {
			document.getElementById("dailyIcon").src=weatherIconDir+message.payloadString+".gif";
			console.log("in icon try");
		}
		catch(err) {
			document.getElementById("dailyIcon").src=weatherIconDir+"na.gif";
			console.log(message.payloadString);
		}
	}
	if (message.destinationName == tempHigh) {
		document.getElementById("tempHigh").innerHTML = Math.round(Number(message.payloadString))+"&deg F";
	}
	if (message.destinationName == tempLow) {
		document.getElementById("tempLow").innerHTML = Math.round(Number(message.payloadString))+"&deg F";
	}
	
	// Control Buttons
	if (message.destinationName == tempSensors + "/house") {
		document.getElementById("desired-temp").innerHTML = message.payloadString;
	}
	
}

// Other functions
function onTempUp() {
	var currentTemp = Number(document.getElementById("desired-temp").innerHTML)
	if (Number.isInteger(currentTemp)) {
		console.log(currentTemp);
		currentTemp = currentTemp + 1;
		console.log(currentTemp);
	}
	else {
		currentTemp = "69";
		console.log(currentTemp + "  in else");
	}
	
	mqtt.publish(tempSensors + "/house", currentTemp.toString(), 1, true);
	document.getElementById("desired-temp").innerHTML = currentTemp.toString();
}

function onTempDown() {
	var currentTemp = Number(document.getElementById("desired-temp").innerHTML)
	if (Number.isInteger(currentTemp)) {
		console.log(currentTemp);
		currentTemp = currentTemp - 1;
		console.log(currentTemp);
	}
	else {
		currentTemp = "69";
		console.log(currentTemp + "  in else");
	}
	
	mqtt.publish(tempSensors + "/house", currentTemp.toString(), 1, true);
	document.getElementById("desired-temp").innerHTML = currentTemp.toString();
}

console.log("connecting to "+ host +" "+ port);	
mqtt = new Paho.MQTT.Client(host,port,"WEATHER");  
var options = {
	cleanSession: false,
	useSSL:true,
	timeout: 3,
	userName:"ziggy",
	password:"ziggy",
	onSuccess: onConnect
};
mqtt.connect(options);
mqtt.onMessageArrived = onMessageArrived;


