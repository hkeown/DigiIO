#!/usr/bin/env python
import time
import os
import glob
import RPi.GPIO as GPIO
import pifacedigitalio
import mysql.connector
from mysql.connector import errorcode
db_config = {
    'user': 'pi',
    'password': 'raspberry',
    'host': '10.0.0.6',
    'database': 'RPiDB'
}

cnx = None
pfd = pifacedigitalio.PiFaceDigital()  # creates a PiFace Digtal object

# Read sensor file
# os.system('modprobe w1-gpio')
# os.system('modprobe w1-therm')

base_dir = None
device_folder = None
device_file = None

LED = 17    # Using BCM 17


def connect_db():
    global cnx

    try:
        print("Connecting to DB...", db_config, time.strftime('%X %x %Z'))
        cnx = mysql.connector.connect(**db_config)

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print('Something is wrong with your user name or password')
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print("DB Connect Error:", err)


def add_temp():  # Insert new temperature
    global pfd

    try:
        pfd.leds[4].turn_on()  # turn on/set high the second LED
        #  GPIO.output(LED, True)

        temp_c, temp_f = read_temp()
        print(temp_c, temp_f, time.localtime())
        cur = cnx.cursor()
        cur.execute("INSERT INTO tempdata VALUES (%s, %s, %s)", (time.localtime(), 'Alex Room', temp_c))
        cnx.commit()
#        GPIO.output(LED, False)
        pfd.leds[4].turn_off()  # turn off high the second LED

        if cur:
            cur.close()

    except mysql.connector.Error as err:
        print("Error: the database is being rolled back. ", err)
        cnx.rollback()


def led_setup():               # Set GPIO Ports
    GPIO.setmode(GPIO.BCM)     # Setup the wiring
    GPIO.setup(LED, GPIO.OUT)  # Setup Ports


def temp_probe_setup():
    # If the sensor is disconnected, the directory will not be created
    # the glob function terminates in a non grafeful manner
    # Check if the directory exists

    try:
        base_dir = '/sys/bus/w1/devices/'
        os.path.isdir(base_dir + '28')  # True/False: check if this is a directory
        device_folder = glob.glob(base_dir + '28*')[0]
        device_file = device_folder + '/w1_slave'
    except:
        print "The Temperature Probe folder has not been created, the probe is not connected\n"
    else:
        print "The Temperature Probe initialised\n"
    finally:
        print "Exiting temp_probe_setup()\n"


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


def main():
    print("Starting...")

    try:
        led_setup()
        temp_probe_setup()
        connect_db()
        while True:
            #  pifacedigitalio.digital_read(pin_number)
            #  pifacedigitalio.digital_write(pin_number, state)
            add_temp()
            time.sleep(5)
    except :
        print("some error")
    finally:
        if cnx:
            cnx.close()
        GPIO.cleanup()


if __name__ == '__main__':
    main()
