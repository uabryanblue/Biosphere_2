"""
Biosphere 2
AUTHOR: Bryan Blue
EMAIL: bryanblue@arizona.edu
STARTED: 2023
Real Time Clock handling
HiLetgo DS3231 + AT24C32N
"""
# HiLetgo DS3231 + AT24C32N
# RTC module default I2C address is 0x57 (dec 87)
# address range is 0x50 to 0x57 using solder jumpers
# https://lastminuteengineers.com/ds3231-rtc-arduino-tutorial/

# TODO this could benefit from trying to initialzie from NTP not available when using ESPNow
# to set the time on the DS3231 use a tuple as shown here
# i2c = I2C(sda=machine.Pin(4), scl=machine.Pin(5))
# d = DS3231(i2c)
# d.set_time((YY, MM, DD, hh, mm, ss, 0, 0))
# example: to set time to 2023, May, 29, 7 am, 11 minutes, 1 second, NA, NA
# d.set_time((2023, 05, 29, 7, 11, 1, 0, 0))

import gc
import time
import machine
import ds3231_gen
gc.collect()
import espnowex
gc.collect()
import realtc
gc.collect()
import conf

def formattime(in_time):
    """time format produce a date/time format from tuple
    only minute resolution supported"""

    # YYYY-MM-DD hh:mm:ss
    date = f'{in_time[0]}-{in_time[1]:0>2}-{in_time[2]:0>2}'
    time = f'{in_time[3]:0>2}:{in_time[4]:0>2}:{in_time[5]:0>2}'
    formatted_time = date + ' ' + time
    
    return formatted_time

def formatrtc(in_time):
    """RTC format time produce a date/time format from tuple
    only minute resolution supported"""
    # rtc.datetime((YY, MM, DD, wday, hh, mm, ss, 0))

    # YYYY-MM-DD hh:mm:ss
    date = f'{in_time[0]}-{in_time[1]:0>2}-{in_time[2]:0>2}'
    time = f'{in_time[4]:0>2}:{in_time[5]:0>2}:{in_time[6]:0>2}'
    formatted_time = date + ' ' + time
    
    return formatted_time

def rtcinit():
    """get the time from the RTC DS3231 board and set the local RTC"""

    rtc = machine.RTC()
    i2c = machine.I2C(sda=machine.Pin(4), scl=machine.Pin(5))
    ds3231 = ds3231_gen.DS3231(i2c)
    YY, MM, DD, hh, mm, ss, wday, _ = ds3231.get_time()
    rtc.datetime((YY, MM, DD, wday, hh, mm, ss, 0))
    gc.collect()
    print(f"DS3231 time: {ds3231.get_time()}")
    print(f"local time: {realtc.formatrtc(rtc.datetime())}")


def get_remote_time(esp_con):
    # set the time from device designated as TIME
    retries = 0
    host = ""
    rtc = machine.RTC()

    peer = bytearray()
    peer = conf.peers["TIME"][0]
    # peer= b'\xc4[\xbe\xe4\xfe=' # TODO debug why not tx work
    espnowex.esp_tx(peer, esp_con, "GET_TIME")
    time.sleep(1)
    host, msg = espnowex.esp_rx(esp_con)
    gc.collect()

    # if a message was not received, loop until a time is received
    while not msg:
        retries += 1
        espnowex.esp_tx(peer, esp_con, "GET_TIME")
        time.sleep(1)
        host, msg = espnowex.esp_rx(esp_con)
        gc.collect()
        print(f"Get Time: unable to get time from {host} retry # {retries}")
        time.sleep(1)

    # print(host)
    str_host = ":".join(["{:02x}".format(b) for b in host])
    # assumption data is utf-8, if not, it may fail
    str_msg = msg.decode("utf-8")

    print("\n------------------------")
    print(f"received a respons from {host} {str_host} of: {msg}")
    evaltime = eval(msg)

    # TODO this should just be rtc from above
    # rtcObj = machine.RTC()
    print(f":::: BEFORE EVAL value {evaltime}")
    rtc.datetime(evaltime)
    gc.collect()
    print(f"The new time is: {realtc.formatrtc(rtc.datetime())}") 
    print("------------------------\n")
