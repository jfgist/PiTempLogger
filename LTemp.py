import os, glob, time, gspread, sys, datetime
import paho.mqtt.client as paho
import json
import struct

device_id = ''
device_secret = ''
random_client_id = ''
 
#Google account details
email = '@gmail.com'
password = ''
spreadsheet = 'Temp_Log2' #the name of the spreadsheet already created 
 
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

def on_message(client, obj, msg):
    # get the JSON message
    json_data = msg.payload
    # check the status property value
    print(json_data)
    value = json.loads(json_data)['properties'][0]['value']
    client.publish(out_topic,json_data)


 
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
#client = paho.Client()

# assign event callbacks
client.on_message = on_message
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
    try:
        # login to google account
        gc = gspread.login(email,password)  

        # open the spreadsheet
        worksheet = gc.open(spreadsheet).sheet1
        
        # get the temp
        temp = read_temp()
        values = [datetime.datetime.now(), temp]

        print('values')
        print(values)
        print('write values to spreadsheet')

        worksheet.append_row(values) #write to the spreadsheet
        payload = { 'properties':[{'id':'54033694bdd5392354000006', 'value':temp }] }
        client.publish(out_topic, json.dumps(payload))
        time.sleep(600) #wait 10 minutes


    except gspread.AuthenticationError:
        print('login failed')
