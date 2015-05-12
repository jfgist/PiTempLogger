#! /usr/bin/python

import json
import urllib2
json_string = urllib2.urlopen("http://192.168.1.40:8037/temperature.json").read()
parsed_json = json.loads(json_string)

print(parsed_json[''])
