#!/usr/bin/python3
#ledtest.py
import glob
import time
import RPi.GPIO as GPIO
import mysql.connector

# RGB LED module
#HARDWARE SETUP
# P1
# 2[======XRG=B==]26
# 1[=============]25
# X=GND R=Red G=Green B=Blue

#Setup Active States
#Common Cathode RGB-LED (Cathode=Active Low)
RGB_ENABLE = 1; RGB_DISABLE = 0

#LED CONFIG - Set GPIO Ports
RGB_RED = 17; RGB_GREEN = 18; RGB_BLUE = 22
#RGB = [RGB_RED,RGB_GREEN,RGB_BLUE]
RGB = [RGB_RED]

def led_setup():
  #Setup the wiring
  GPIO.setmode(GPIO.BCM)
  #Setup Ports
  for val in RGB:
    GPIO.setup(val,GPIO.OUT)

#Read sensor file
#os.system('modprobe w1-gpio')
#os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos + 2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_c, temp_f


#while True:
#    print(read_temp())
#    time.sleep(1)

# http put request
#r = requests.get('http://www.omdbapi.com/?t=Die+Hard&y=1988&plot=short&r=json')
#print(r.text)

#MYSQL
#cnx = mysql.connector.connect(user='weather', password='password', host='192.168.5.138', database='weather')
#cursor = cnx.cursor()
#query = ("SELECT id, temperature FROM PiWeather")
#cursor.execute(query)

#for (id, temperature) in cursor:
#   print (id, temperature)

#cursor.close()
#cnx.close()



def main():
  led_setup()

  for i in range(10):
    print (i)
    for val in RGB:
      GPIO.output(val,RGB_ENABLE)
      print("LED ON")
      time.sleep(2)

      print(read_temp())
      time.sleep(1)

      GPIO.output(val,RGB_DISABLE)
      print("LED OFF")
      time.sleep(2)

try:
  main()
finally:
  GPIO.cleanup()
  print("Closed Everything. END")




#End
