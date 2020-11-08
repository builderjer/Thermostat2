// This script controls the mqtt client and subscribes to several aspects
// of the weather.
// It pulls it's information from DarkSky API

var __author__ = "builderjer"
var __version__ = "0.1.0"

var mqtt;
var reconnectTimeout = 2000;
var host="192.168.0.254" ;
var port=9001;

// var weatherIconDir = "../assets/images/weather/icon-set/GIF/50x50/";
//
// var currentSummary = "ziggy/weather/current/summary";
// var currentIcon = "ziggy/weather/current/icon";
var currentTemp = "ziggy/weather/current/temp";
var desiredTemp = "ziggy/climate/temp/desired";
var heaterState = "ziggy/climate/heater";
var thermostatMode = "ziggy/climate/thermostat/mode"
// var dailySummary = "ziggy/weather/daily/summary";
// var dailyIcon = "ziggy/weather/daily/icon";
// var tempHigh = "ziggy/weather/daily/tempHigh";
// var tempLow = "ziggy/weather/daily/tempLow";
// var weeklySummary = "ziggy/weather/weekly/summary";
//
// var weather = "ziggy/weather/#";
//
// //var tempSensors = "ziggy/house/climate/temp/#";
var houseTemp = "ziggy/climate/temp/house";

// called when the client connects
function onConnect() {
	// Once a connection has been made, make a subscription and send a message.
	// mqtt.subscribe(weather, {"qos": 1});
	// mqtt.subscribe(houseTemp, {"qos": 1});
	console.log("connected mqtt")

// 	mqtt.subscribe(temp, {"qos":1});
// 	mqtt.subscribe(tempHigh, {"qos":1});
// 	mqtt.subscribe(tempLow, {"qos":1});
// 	mqtt.subscribe(icon, {"qos":1});
// 	mqtt.subscribe(sunrise, {"qos":1});
// 	mqtt.subscribe(sunset, {"qos":1});
	mqtt.subscribe(currentTemp, {"qos":1});
	mqtt.subscribe(desiredTemp, {"qos":1});
	mqtt.subscribe(heaterState, {"qos":1});
	mqtt.subscribe(houseTemp, {"qos":1});
	mqtt.subscribe(thermostatMode, {"qos":1});
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

// 	// Current Readings
// 	if (message.destinationName == currentSummary) {
// 		document.getElementById("currentSummary").innerHTML = message.payloadString;
// 	}
//
// 	if (message.destinationName == currentIcon) {
// 		try {
// 			document.getElementById("currentIcon").src=weatherIconDir+message.payloadString+".gif";
// 		}
// 		catch(err) {
// 			document.getElementById("currentIcon").src=weatherIconDir+"na.gif";
// 			console.log(message.payloadString);
// 		}
// 	}
	if (message.destinationName == currentTemp) {
		document.getElementById("currentTemp").innerHTML = Math.round(Number(message.payloadString))+"&deg F";
		console.log(message.payloadString + " current temp call");
	}

	if (message.destinationName == desiredTemp) {
		console.log("dTemp: " + message.payloadString);
		document.getElementById("desiredTemp").innerHTML = message.payloadString.toString()+"&deg F";
		// mqtt.send(desiredTemp, message.payloadString.toString())
	}

	if (message.destinationName == thermostatMode) {
		document.getElementById("thermostatMode").innerHTML = message.payloadString;
	}

	if (message.destinationName == heaterState) {
		const HI = document.getElementById("heatIndicator");
		if (message.payloadString == "ON") {
			HI.setAttribute("class", "lg-txt");
			HI.innerHTML = "HEAT ON";
		}
		else if (message.payloadString == "OFF") {
			HI.setAttribute("class", "md-txt");
			HI.innerHTML = "HEAT OFF";
		}
	}

	if (message.destinationName == houseTemp) {
		document.getElementById("indorTemp").innerHTML = message.payloadString + "&deg F";
	}
//
// 	// Daily forecast
// 	if (message.destinationName == dailySummary) {
// 		document.getElementById("dailySummary").innerHTML = message.payloadString;
// 	}
// 	if (message.destinationName == dailyIcon) {
// 		try {
// 			document.getElementById("dailyIcon").src=weatherIconDir+message.payloadString+".gif";
// 		}
// 		catch(err) {
// 			document.getElementById("dailyIcon").src=weatherIconDir+"na.gif";
// 			console.log(message.payloadString);
// 		}
// 	}
// 	if (message.destinationName == tempHigh) {
// 		document.getElementById("tempHigh").innerHTML = Math.round(Number(message.payloadString))+"&deg F";
// 	}
// 	if (message.destinationName == tempLow) {
// 		document.getElementById("tempLow").innerHTML = Math.round(Number(message.payloadString))+"&deg F";
// 	}
//
// 	// Control Buttons
// 	if (message.destinationName == houseTemp) {
// 		document.getElementById("indoor-temp").innerHTML = message.payloadString;
// 	}
// }
}
// Other functions
function onTempUp() {
	var dTemp = parseInt(document.getElementById("desiredTemp").innerHTML);
	console.log(typeof dTemp + "  " + dTemp.toString());
	// if (Number.isInteger(currentTemp)) {
	if (typeof dTemp === "number") {
		console.log("hello there " + dTemp.toString());
		dTemp = dTemp + 1;
		console.log(dTemp.toString());
		mqtt.publish(desiredTemp, dTemp.toString());

	}
	// if (Number.isInteger(currentTemp)) {
	// 	console.log(currentTemp);
	// 	currentTemp = currentTemp + 1;
	// 	console.log(currentTemp);
	// 	client.send(desiredTemp, currentTemp);
	// }
	// else {
	// 	currentTemp = "Sensor Down";
	// }

	document.getElementById("desiredTemp").innerHTML = dTemp.toString();
}

function onTempDown() {
	var dTemp = parseInt(document.getElementById("desiredTemp").innerHTML);
	console.log(typeof dTemp + "  " + dTemp.toString());
	// if (Number.isInteger(currentTemp)) {
	if (typeof dTemp === "number") {
		console.log("hello there " + dTemp.toString());
		dTemp = dTemp - 1;
		console.log(dTemp.toString());
		mqtt.publish(desiredTemp, dTemp.toString());
	}


	document.getElementById("desiredTemp").innerHTML = dTemp.toString();
}

console.log("connecting to "+ host +" "+ port);
mqtt = new Paho.MQTT.Client(host,port,"WEATHER");
var options = {
	cleanSession: false,
	// useSSL:true,
	timeout: 3,
	// userName:"ziggy",
	// password:"ziggy",
	onSuccess: onConnect
};
mqtt.connect(options);
mqtt.onMessageArrived = onMessageArrived;
