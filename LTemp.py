import os, glob, time, sys, datetime
import paho.mqtt.client as paho
import json

device_id = ''
device_secret = ''
random_client_id = ''
 
#initiate the temperature sensor
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
 
#set up the location of the sensor in the system
print('get device folder')
device_folder = glob.glob('/sys/bus/w1/devices/28*')[0]
device_file = device_folder + '/w1_slave'
 
#connection event
def on_connect(client, data, flags, rc):
    print('Connected, rc: ' + str(rc))

#subscription event
def on_subscribe(client, userdata, mid, gqos):
    print('Subscribed: ' + str(mid))

# Shouldn't be receiving messages to this device
# def on_message(client, obj, msg):

def read_temp_raw(): #a function that grabs the raw temperature data from the sensor
    print('read temperature')
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines
 
 
def read_temp(): #a function that checks that the connection was good and strips out the temperature
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000
        temp_f = temp_c * 9.0 / 5.0 + 32.0
    return temp_f

# create the MQTT client
client = paho.Client(client_id='rando', protocol=paho.MQTTv31)

# assign event callbacks
# client.on_message = on_message
client.on_connect = on_connect
client.on_subscribe = on_subscribe

# device topics
in_topic = 'devices/' + device_id + '/get' # receiving messages
out_topic = 'devices/' + device_id + '/set' # publishing messages

# client connection
client.username_pw_set(device_id, device_secret) # MQTT server credentials
client.connect("178.62.108.47")			 # MQTT server address
client.subscribe(in_topic,0)
 
while True: #infinite loop
    client.loop()
    # get the temp
    temp = read_temp()
    values = [datetime.datetime.now(), temp]

    print('values')
    print(values)
    payload = { 'properties':[{'id':'54033694bdd5392354000006', 'value':temp }] }
    client.publish(out_topic, json.dumps(payload))
    time.sleep(600) #wait 10 minutes
