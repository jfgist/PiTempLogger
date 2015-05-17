#! /usr/bin/python

import json
import urllib2
json_string = urllib2.urlopen("http://192.168.1.40:8037/temperature.json").read()
print json_string
parsed_json = json.loads(json_string)
print parsed_json

s = parsed_json['status']
print s

f = parsed_json['temperature']['fahrenheit']
print f

c = parsed_json['temperature']['celsius']
print c

