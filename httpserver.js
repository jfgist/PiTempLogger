/******************************************************************************
* Intructions:
* The temperature readings rely on the 1-wire module being loaded.
*   $ modprobe w1-gpio
*   $ modprobe w1-therm  # not sure if this is really needed.
* It is better to add those two modules to /etc/modules so they load at boot.
* 
* The 1-wire module uses pin #4 on the Pi by default.
* 
* The sensor address is hard-coded here and must be set for the sensor in use.
* There may be a way to scan and just grab the first temp sensor found.
* 
* The 1-wire output may have a 'Yes' or 'No' at the end so I should parse that
* at some point.
******************************************************************************/

var http = require('http');
var fs = require('fs');
var url = require('url');
var exec=require('child_process').exec;
//var tempAddress = '28-00000690f080';
var tempAddress = '28-0000068fa54a';
var tempLocation = '/sys/bus/w1/devices/' + tempAddress + '/w1_slave';
var verbose = true;

http.createServer(function (req, res) {
  var request_url = url.parse(req.url).pathname;
  if(verbose) console.log("Request from " + req.connection.remoteAddress +
    ": " + request_url);

  if (request_url == '/temperature.json') {
    fs.readFile(tempLocation, 'utf8', function(err, data) {
      res.writeHead(200, { 'Content-Type': 'application/json' });
      // if (err) throw err;
      if(err) {
        output = '{"status": "tempError"}'; 
      } else {
        matches = data.match(/t=([0-9]+)/);
        temperatureC = parseInt(matches[1]) / 1000;
        temperatureF = ((temperatureC * 1.8) + 32).toFixed(3);
        output = '{"status": "tempSuccess",' +
	         '"temperature": {"celsius": ' + temperatureC + ',' +
                                  '"fahrenheit": ' + temperatureF + ' } }';
      }
      res.end(output);
    });
  } else {
    res.writeHead(200, {'Content-Type': 'text/plain'});
    res.end('No route');
  }
}).listen(8037);

console.log('Server running on port 8037');
