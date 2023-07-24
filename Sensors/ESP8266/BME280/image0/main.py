
# Complete project details at https://RandomNerdTutorials.com

import time
from machine import Pin, I2C, RTC
import realtc

import BME280
import espnowex

print("START SENSOR")


# con = espnowex.init_esp_connection()
sta, ap = espnowex.wifi_reset()
esp_con = espnowex.init_esp_connection(sta)

# convert hex into readable mac address
RAW_MAC = espnowex.get_mac(sta)
MY_MAC = ':'.join(['{:02x}'.format(b) for b in RAW_MAC])
# print(f"My MAC:: {MY_MAC}")
print(f"My MAC addres:: {MY_MAC} raw MAC:: {RAW_MAC}")

# set the time from the logger
retries = 0
host = ''
espnowex.esp_tx(b'\xc4[\xbe\xe4\xfe=', esp_con, 'get_time')
host, msg = espnowex.esp_rx(esp_con)

while not msg:
    retries += 1
    espnowex.esp_tx(b'\xc4[\xbe\xe4\xfe=', esp_con, 'get_time')
    # print("Time Sensor: wait for time response")
    host, msg = espnowex.esp_rx(esp_con)
    print(f'found host: {host}')        
    print(f"Get Time: unable to get time ({retries})")
    time.sleep(3)

print(host)
str_host = ':'.join(['{:02x}'.format(b) for b in host])
# assumption data is utf-8, if not, it may fail
str_msg = msg.decode('utf-8')

print("------------------------")
print(f"received a respons from {host} {str_host} of: {msg}") 
et = eval(msg)
print("--------------------")
print(f"et: {et}")
print("--------------------")

rtc = RTC()
rtc.datetime(et)
print(f"Climate Sensor: the new time is: {realtc.formattime(time.localtime())}")  



# ESP32 - Pin assignment
# i2c = I2C(scl=Pin(22), sda=Pin(21), freq=10000)
# ESP8266 - Pin assignment
i2c = I2C(scl=Pin(5), sda=Pin(4), freq=10000)

print("i2c INITIALZED")

sequence = 1 # record number from the last time the system restarted

while True:
    bme = BME280.BME280(i2c=i2c)
    temperature = bme.temperature
    Humidity = bme.humidity
    Pressure = bme.pressure
    # uncomment for temperature in Fahrenheit
    #temp = (bme.read_temperature()/100) * (9/5) + 32
    #temp = str(round(temp, 2)) + 'F'

    # print('Temperature: ', temperature)
    # print('Humidity: ', Humidity)
    # print('Pressure: ', Pressure)

    Message = f'{temperature}, {Humidity}, {Pressure}'
    date_time = realtc.formattime(time.localtime())
    out = str(sequence) + ', ' + date_time + ', ' + Message
    print(out)
    espnowex.esp_tx(b'\xc4[\xbe\xe4\xfe=', esp_con, out)
    sequence += 1

    time.sleep(15)
