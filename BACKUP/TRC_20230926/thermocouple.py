# import machine
from machine import Pin, SPI
from math import isnan
from time import sleep
import struct
import conf
# import max31855


def parse_max318855(data):
    """translate binary response into degreee C"""

    # Binary reading of data based on MAX318855 library by Diego Herranz, 2013
    # modified for MicroPython
    fault = struct.unpack("B", data[1:3])[0] & 0x01
    if fault:
        return float("NaN"), float("NaN")

    # Thermo-couple temperature
    temperature = struct.unpack(">h", data[0:2])[0] >> 2;  # >h = signed short, big endian. 14 leftmost bits are data.    
    temperature = temperature / (2**2)  # Two binary decimal places

    # Internal temperature
    internal_temperature = struct.unpack(">h", data[2:4])[0] >> 4;  # >h = signed short, big endian. 12 leftmost bits are data.  
    internal_temperature = internal_temperature / (2**4)  # Four binary decimal places

    return temperature, internal_temperature



def callibrated_reading(deviceId, temperature):
    """thermocouples may need callibrated
    coefficients should be stored in the config file
    2nd order can be used if non-linear
    set first coeficient to 0 for linear"""
    # TODO need to pass in callibration parameters defined in some config file
    # callibrate each thermocouple using 2nd order polynomial
    # for linear, set first coefficiet to 0
    beta0 = conf.callibrations[deviceId][1]
    beta1 = conf.callibrations[deviceId][2]
    beta2 = conf.callibrations[deviceId][3]
    tempCorrected = (beta0 + (beta1 * temperature) + (beta2 * temperature * temperature)) 

    return tempCorrected

def initReadings(readings):
    for key in readings.keys():
        readings[key][2] = 0.0 # position is temp value
    return readings

def catReadings(readings):
    strReadings = ''
    for key in readings.keys():
        strReadings =+ readings[key][2] # 2nd position is temp value
    return strReadings

def thermocouples_off():
    # returns all TP 1 - 5 on the board off
    # reads on low values, 'on' is off value
    S0 = Pin(16, Pin.OUT)
    S0.on()
    S1 = Pin(5, Pin.OUT)
    S1.on()
    S2 = Pin(4, Pin.OUT)
    S2.on()
    S3 = Pin(0, Pin.OUT)
    S3.on()
    S4 = Pin(2, Pin.OUT)
    S4.on()

def read_thermocouple(cs_pin, spi):
    """reads one thermocouple from given CS pin and spi object"""
    raw_data = bytearray(4)

    # turn off all thermocouples
    thermocouples_off()

    if cs_pin == 1:
        S0 = Pin(16, Pin.OUT)
        S0.off()
    elif cs_pin == 2:
        S1 = Pin(5, Pin.OUT)
        S1.off()
    elif cs_pin == 3:
        S2 = Pin(4, Pin.OUT)
        S2.off()
    elif cs_pin == 4:
        S3 = Pin(0, Pin.OUT)
        S3.off()
    elif cs_pin == 5:
        S4 = Pin(2, Pin.OUT)
        S4.off()

    sleep(0.250) # 250 ms
    spi.readinto(raw_data)
    temperature, internal = parse_max318855(raw_data)

    # turn off all thermocouples
    thermocouples_off()
    return temperature, internal

def allReadings(readings, prefix=''):
    """join all reading values in the order specified by the configuration values in readsingsOrder
    prefix is the default for the output string and should not contain a delimiter"""
    out = prefix + ","
    for item in conf.readingsOrder:
        TempOut = ','.join([str(readings[item][2]) for item in conf.readingsOrder])  # real temperatures
        IntOut =  ','.join([str(readings[item][4]) for item in conf.readingsOrder])  # internal temperatures

    return TempOut, IntOut


def read_thermocouples(readings):
    """setup spi connection, read all thermocouples, close spi connection
    nan values are only given if all values that are read are nan otherwise
    the average of all readings not nan are returned"""
    # create variable to do averages based on readings structure
    myReadings = readings
    # initialization for those values that need to be reset
    for key in myReadings.keys():
        myReadings[key][2] = 0.0 # position is cumulative temp value
        myReadings[key][3] = 0   # position is reading count for averaging
        myReadings[key][4] = 0.0 # position is cumulative internal temp value
    
    tspi = SPI(1, baudrate=5000000, polarity=0, phase=0)
    numSamples = 3 # specifiy the number of readings to take and average
    for i in range(numSamples):
        for key in readings.keys():
            cs_pin = readings[key][0] # first position is pin number
            temperature, internal_temperature = read_thermocouple(cs_pin, tspi)

            if not isnan(temperature): # only increment true values and ignore nan values
                myReadings[key][2] += temperature
                myReadings[key][3] += 1
                myReadings[key][4] += internal_temperature

            # sleep(0.50) # delay before next reading, can be modified        

    for key in readings.keys():
        if myReadings[key][3] > 0:  #  position 3 is number of successful reads for averaging
            avgReading = round(myReadings[key][2] / myReadings[key][3], 2)
            avgInternalReading = round(myReadings[key][4] / myReadings[key][3], 2)
            # calReading = callibrated_re?eading(myReadings[key][3], avgReading)
            # print(f"data key: {myReadings[key][3]}   key: {key}   avg: {avgReading}   cal: {calReading}")
            readings[key][2] = avgReading
            readings[key][4] = avgInternalReading
            
        else: # we didn't take any readings, therefore not a number
            readings[key][2] = float("NaN")
            readings[key][4] = float("NaN")
                  
    # turn all of the thermocouple sensors off when not in use
    thermocouples_off()

    tspi.deinit()

    return readings, myReadings
