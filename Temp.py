import os, glob, time, gspread, sys, datetime
 
#Google account details
email = 'foo.bar@gmail.com'
password = 'Foo_Bars_Password'
spreadsheet = 'Temperature_log' #the name of the spreadsheet already created
 
#attempt to log in to your google account
try:
    gc = gspread.login(email,password)
except:
    print('fail')
    sys.exit()
 
#open the spreadsheet
worksheet = gc.open(spreadsheet).sheet1
 
#initiate the temperature sensor
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
 
#set up the location of the sensor in the system
device_folder = glob.glob('/sys/bus/w1/devices/28*')
device_file = [device_folder[0] + '/w1_slave', device_folder[1] + '/w1_slave']
 
 
def read_temp_raw(): #a function that grabs the raw temperature data from the sensor
    f_1 = open(device_file[0], 'r')
    lines_1 = f_1.readlines()
    f_1.close()
    f_2 = open(device_file[1], 'r')
    lines_2 = f_2.readlines()
    f_2.close()
    return lines_1 + lines_2
 
 
def read_temp(): #a function that checks that the connection was good and strips out the temperature
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES' or lines[2].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t='), lines[3].find('t=')
    temp = float(lines[1][equals_pos[0]+2:])/1000, float(lines[3][equals_pos[1]+2:])/1000
    return temp
 
while True: #infinite loop
    temp = read_temp() #get the temp
    values = [datetime.datetime.now(), temp[0], temp[1]]
    worksheet.append_row(values) #write to the spreadsheet
    time.sleep(600) #wait 10 minutes
