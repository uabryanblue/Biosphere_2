# import machine
from machine import Pin, SPI
from math import isnan
from time import sleep
import conf


def temp_c(data):
    """translate binary response into degreee C"""
    temp = data[0] << 8 | data[1]
    if temp & 0x0001:
        return float("NaN")  # Fault reading data.
    temp >>= 2
    if temp & 0x2000:
        temp -= 16384  # Sign bit set, take 2's compliment.
    return temp * 0.25


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
        readings[key][2] = 0.0 # 3rd position is temp value
    return readings

def catReadings(readings):
    strReadings = ''
    for key in readings.keys():
        strReadings =+ readings[key][2] # 2nd position is temp value
    return strReadings

def read_thermocouple(cs_pin, spi):
    """reads one thermocouple from given CS pin and spi object"""
    raw_data = bytearray(4)

    S0 = Pin(16, Pin.OUT)
    S0.on()
    S1 = Pin(5, Pin.OUT)
    S1.on()
    S2 = Pin(4, Pin.OUT)
    S2.on()
    S3 = Pin(0, Pin.OUT)
    S3.on()
    S4 = Pin(2, Pin.OUT)
    S4.on() # signal low to read, default high

    # brute force testing
    if cs_pin == 1:
        S0.off()
        S1.on()
        S2.on()
        S3.on()
        S4.on()
    elif cs_pin == 2:
        S0.on()
        S1.off()
        S2.on()
        S3.on()
        S4.on()
    elif cs_pin == 3:
        S0.on()
        S1.on()
        S2.off()
        S3.on()
        S4.on()
    elif cs_pin == 4:
        S0.on()
        S1.on()
        S2.on()
        S3.off()
        S4.on()
    elif cs_pin == 5:
        S0.on()
        S1.on()
        S2.on()
        S3.on()
        S4.off()

    sleep(0.250) # 250 ms
    spi.readinto(raw_data)
    temp = temp_c(raw_data)

    return temp

def allReadings(readings, prefix=''):
    """join all reading values in the order specified by the configuration values in readsingsOrder
    prefix is the default for the output string and should not contain a delimiter"""
    out = prefix + ","
    for item in conf.readingsOrder:
        out = ','.join([str(readings[item][2]) for item in conf.readingsOrder])
    return out


def read_thermocouples(readings):
    """setup spi connection, read all thermocouples, close spi connection
    nan values are only given if all values that are read are nan otherwise
    the average of all readings not nan are returned"""
    # create variable to do averages based on readings structure
    myReadings = readings
    # initialization for those values that need to be reset
    for key in myReadings.keys():
        myReadings[key][2] = 0.0 # 3rd position is cumulative temp value
        myReadings[key][1] = 0   # 2nd position is reading count for averaging
    
    tspi = SPI(1, baudrate=5000000, polarity=0, phase=0)
    numSamples = 10 # specifiy the number of readings to take and average
    for i in range(numSamples):
        for key in readings.keys():
            cs_pin = readings[key][0] # first position is pin number
            tRead = read_thermocouple(cs_pin, tspi)

            if not isnan(tRead): # only increment true values and ignore nan values
                myReadings[key][2] += tRead
                myReadings[key][1] += 1

            sleep(0.250) # 250 ms delay before next reading, can be modified
        print(allReadings(readings)) # TODO debug output

    for key in readings.keys():
        if myReadings[key][1] > 0:
            avgReading = round(myReadings[key][2] / myReadings[key][1], 2)
            # calReading = callibrated_re?eading(myReadings[key][3], avgReading)
            # print(f"data key: {myReadings[key][3]}   key: {key}   avg: {avgReading}   cal: {calReading}")
            readings[key][2] = avgReading
            
        else: # we didn't take any readings, therefore not a number
            readings[key][2] = float("NaN")
                  
    # TODO put in some error checking to ensure spi is released
    tspi.deinit()

    return readings, myReadings
