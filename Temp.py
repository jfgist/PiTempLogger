import os, glob, time, gspread, sys, datetime
 
#Google account details
email = ''
password = ''
spreadsheet = '' #the name of the spreadsheet already created 
 
#initiate the temperature sensor
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
 
#set up the location of the sensor in the system
print('get device folder')
device_folder = glob.glob('/sys/bus/w1/devices/28*')[0]
device_file = device_folder + '/w1_slave'
 
 
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
 
while True: #infinite loop

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
        time.sleep(600) #wait 10 minutes

    except gspread.AuthenticationError:
        print('login failed')
