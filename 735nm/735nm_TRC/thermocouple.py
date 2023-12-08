import gc
from machine import Pin, SPI
from math import isnan
gc.collect()
import time
import struct
import conf
# import max31855
gc.collect()

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
    gc.collect()

    return temperature, internal_temperature



def calibrate_reading(key, temperature):
    """thermocouples may need callibrated
    coefficients should be stored in the config file
    2nd order can be used if non-linear
    set first coeficient to 0 for linear"""
    # TODO need to pass in callibration parameters defined in some config file
    # callibrate each thermocouple using 2nd order polynomial
    # for linear, set 3rd coefficiet to 0
    # callibrations['TREATMENT'] = ["T118", 1, 28.33, -11.692, 0]
    # = [TCID, PORT, offset, slope, x^2]
    if temperature > 0:
        beta0 = conf.callibrations[key][2]
        beta1 = conf.callibrations[key][3]
        beta2 = conf.callibrations[key][4]
        tempCorrected = (beta0 + (beta1 * temperature) + (beta2 ** temperature)) 
    else:
        tempCorrected = temperature
    gc.collect()

    return tempCorrected

# def initReadings(readings):
#     for key in readings.keys():
#         readings[key][2] = 0.0 # position is temp value
#     return readings

def initReadings(readings):
    for key in readings.keys():
        readings[key][2] = 0.0 # position is cumulative temp value
        readings[key][3] = 0   # position is reading count for averaging
        readings[key][4] = 0.0 # position is cumulative internal temp value
    return readings

def createReadings(t):   
    # create a NEW storage location with 0 values
    t['TREATMENT'] = [1, 16, 0.0, 0, 0.0]
    t['CONTROL'] = [2, 5, 0.0, 0, 0.0]
    t['REFERENCE'] = [3, 4, 0.0, 0, 0.0]
    t['HEAT'] = [4, 0, 0.0, 0, 0.0]
    t['CONTROL_HEAT'] = [5, 2, 0.0, 0, 0.0]
    return t

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

    time.sleep_ms(250) # 250 ms
    spi.readinto(raw_data)
    temperature, internal = parse_max318855(raw_data)
    gc.collect()

    # turn off all thermocouples
    thermocouples_off()
    return temperature, internal

def allReadings(readings, prefix=''):
    """join all reading values in the order specified by the configuration values in readsingsOrder
    prefix is the default for the output string and should not contain a delimiter"""
    out = prefix + ","
    for item in conf.readingsOrder:
        TempOut = ','.join([str(readings[item][2]) for item in conf.readingsOrder])  # real temperatures
        CJOut =  ','.join([str(readings[item][4]) for item in conf.readingsOrder])  # internal temperatures


    return TempOut, CJOut

def readThermocouples(tspi):
    # print(f"\n        READING TC VALUES           \n")
    """setup spi connection, read all thermocouples, close spi connection
    nan values are only given if all values that are read are nan otherwise
    the average of all readings not nan are returned"""
    # create variable to do averages based on readings structure
    tcReadings = conf.readings # just for calculations
    tcReadings = initReadings(tcReadings)
    
    # do one read, main loop for multiple
    numSamples = conf.TC_READS # specifiy the number of readings to take and average
    for i in range(numSamples):
        for key in tcReadings.keys():
            cs_pin = tcReadings[key][0] # first position is pin number
            temperature, internal_temperature = read_thermocouple(cs_pin, tspi)
            # print(f"{key}  TC {temperature}, CJ {internal_temperature}")
            if not isnan(temperature): # only increment true values and ignore nan values
                tcReadings[key][2] += temperature
                tcReadings[key][3] += 1 # this only increments when a valid temp is read
                tcReadings[key][4] += internal_temperature
            else:
                print(f"   bad read 1 TC {key:12} {tcReadings[key][2]:5}  {tcReadings[key][3]:5}  {tcReadings[key][4]:5}")
            # sleep(0.50) # delay before next reading, can be modified        
    gc.collect()
    calReadings = {}
    for key in tcReadings.keys():
        if tcReadings[key][3] > 0:  #  position 3 is number of successful reads for averaging
            tcReadings[key][2] = round(tcReadings[key][2] / tcReadings[key][3], 2)
            tcReadings[key][4] = round(tcReadings[key][4] / tcReadings[key][3], 2)
            tcReadings[key][3] = 1 # only one averaged reading is returned
            calReadings[key] = calibrate_reading(key, tcReadings[key][2])
            # print(f"{calReadings}")
            print(f"TC Pos: {conf.callibrations[key][1]:4} TC: {conf.callibrations[key][0]:6}   key: {key:13}   avg: {conf.readings[key][2]:8}   cal: {calReadings[key]:8}")
        
        else: # we didn't take any readings, therefore not a number
            tcReadings[key][2] = float("NaN")
            tcReadings[key][4] = float("NaN")
            tcReadings[key][3] = 0 # error after avg readings, 0, no readings
            calReadings[key] = float("NaN")
                  
    # turn all of the thermocouple sensors off when not in use
    thermocouples_off()

    # tspi.deinit()

    return  tcReadings, calReadings
