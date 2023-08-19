"""
Biosphere 2
AUTHOR: Bryan Blue
EMAIL: bryanblue@arizona.edu
STARTED: 2023
"""
# HiLetgo DS3231 + AT24C32N
# RTC module default I2C address is 0x57 (dec 87)
# address range is 0x50 to 0x57 using solder jumpers
# https://lastminuteengineers.com/ds3231-rtc-arduino-tutorial/

# TODO this could benefit from trying to initialzie from NTP not available when using ESPNow
# to set the time on the DS3231 use a tuple as shown here
# i2c = machine.I2C(sda=machine.Pin(4), scl=machine.Pin(5))
# d = DS3231(i2c)
# d.set_time((YY, MM, DD, hh, mm, ss, 0, 0))
# example: to set time to 2023, May, 29, 7 am, 11 minutes, 1 second, NA, NA
# d.set_time((2023, 05, 29, 7, 11, 1, 0, 0))

from machine import I2C, Pin, RTC
import time
from ds3231_gen import *
import gc


def formattime(in_time):
    """produce a date/time format from tuple
    only minute resolution supported"""

    # YYYY-MM-DD hh:mm:ss
    date = f'{in_time[0]}-{in_time[1]:0>2}-{in_time[2]:0>2}'
    time = f'{in_time[3]:0>2}:{in_time[4]:0>2}:{in_time[5]:0>2}'
    formatted_time = date + ' ' + time

    return formatted_time

def rtcinit():
    """get the time from the RTC DS3231 board and set the local RTC"""
    gc.collect()

    rtc = RTC()
    i2c = I2C(sda=machine.Pin(4), scl=machine.Pin(5))
    d = DS3231(i2c)
    YY, MM, DD, hh, mm, ss, wday, _ = d.get_time()
    rtc.datetime((YY, MM, DD, wday, hh, mm, ss, 0))
    print(f"DS3231 get_time(): {d.get_time()}")
    print(f"time localtime(): {formattime(time.localtime())}")
    print(f"RTC datetime(): {rtc.datetime()}")


###########################
# TURN ON LATER FOR ntp WiFi SUPPORT
# this is old code and needs reworked

# import network
# import ntptime

# # this is a config file to be used to pass values that can change dynamically
# import conf

# try:
#     import usocket as socket
# except:
#     import socket

# gc.collect()
# # setup netword connection
# station = network.WLAN(network.STA_IF)
# station.active(True)
# station.connect(conf.WAP_SSID, conf.WAP_PSWD)
# while station.isconnected() is False:
#     pass
# print("Connection successful")
# print(f"STATION: {station.ifconfig()}")

# # set current date time with appropriate offset for timezone -7 is Tucson
# ntptime.host = conf.NTP_HOST
# try:
#     print(f"Local time before NTP: {str(time.localtime())}")
#     ntptime.settime()
#     print(f"Local time after NTP: {str(time.localtime(time.time() + conf.UTC_OFFSET))}")
# except:
#     print("Error syncing time")

# initialize pin for led control
# led = Pin(2, Pin.OUT)
# # initialize the led as on
# led.on()
