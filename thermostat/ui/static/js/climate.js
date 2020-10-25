var __author__ = "builderjer"
var __version__ = "0.1.0"

var mqtt;
var reconnectTimeout = 2000;
var host="ziggyhome.mooo.com" ;
var port=8183;

var tempSensors = "ziggy/house/climate/temp";

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
	document.getElementById("desired-temp").innerHTML = "down";
}

function onConnect() {
	console.log("onConnect");
	mqtt.subscribe(tempSensors + "/#", {"qos": 1});
}

function onMessageArrived(message) {
	if (message.destinationName == tempSensors + "/house") {
		document.getElementById("desired-temp").innerHTML = message.payloadString;
	}
}


mqtt = new Paho.MQTT.Client(host,port,"CLIMATE");  
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
