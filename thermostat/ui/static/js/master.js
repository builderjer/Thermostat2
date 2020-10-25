// My custom javascript file.  Hope I can get this to work!!

// Author:  Jeremy Brodie
// Email:  builderjer@gmail.com
// Version:  0.0.1

// // New test for running python process
// const { spawn } = require("child_process");

// Establish some variables

var clockTimer = setInterval(function(){ clockDisplay() }, 1000);
var weatherTimer = setInterval(function(){ weatherDisplay() }, 20 * 6000);

function clockDisplay() {
  var dt = new Date();
	var sc = dt.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
	var sd = dt.toLocaleDateString();
	var lc = dt.toLocaleTimeString();
	var ld = dt.toLocaleDateString([], {weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'});

	try {
    	document.getElementById("short-clock").innerHTML = sc;
	}
	catch(TypeError) {
		document.getElementById("long-clock").innerHTML = lc;
	}

	try {
		document.getElementById("short-date").innerHTML = sd;
	}
	catch(TypeError) {
		document.getElementById("long-date").innerHTML = ld;
	}
}

function weatherDisplay() {
  var dailyHighTemp
}
