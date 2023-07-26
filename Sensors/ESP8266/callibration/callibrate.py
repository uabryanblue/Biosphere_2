""" This script is for interactive callibration of thermocouples
    It needs to be run from the REPL 
    From the conf.py file is a dict of values
    KEY - the thermocouple identifier, numeric
    1 - the connection position. If you had 5 connections possible
        you may put the numer identifier in this location
    The next three values are coefficients for a linear or quadratic
        equation. Leave the last value 0 for linear.
    Position 1 is the intercept  Y = mx + b  it is 'b'
    Position 2 is the 'm' value from y = mx + b
    Position 3 is for an optional squared term for a quadratic function
    callibrations[101] = [1, 28.5, 0.262, 0]
    """
    
import conf
import thermocouple
# import logger
import sys
import machine
import math

NUM_READINGS = 10 # the number of consecutive readings that must fall within VARIANCE
VARIANCE = 0.5 # how far NUM_READINGS values must be before accepting reading
READ_TIMEOUT = 100 # number of readings to take before failing to callibrate

def variance(lst):
    avg = sum(lst) / len(lst)
    var = sum((x-avg)**2 for x in lst) / len(lst)
    return var

def callibrate(BoardPos, TCId):
    readings = thermocouple.initReadings(conf.readings) # should not be needed, testing
    temperature_data, internal_data = thermocouple.allReadings(readings)
    print(temperature_data)
    return []

    read_count = 0
    TRead = []
    TVar = 0.0
    tspi = machine.SPI(1, baudrate=5000000, polarity=0, phase=0)
    print(tspi)
    # read the first NUM_READINGS to calculate variance
    print(f'Taking temperature readings from board {BoardPos}')
    for cnt in range(NUM_READINGS):
        temperature, internalTemp = thermocouple.read_thermocouple(BoardPos, tspi)
        if not math.isnan(temperature): 
            TRead.append(temperature)
        else:
            print(f'NaN reading given, check your connections on board position {BoardPos} and try again.')
            tspi.deinit()
            break
    print(f'first {NUM_READINGS} are {TRead}')
    # TVar = variance(TRead)
    print(f"varince first 10: {TVar}")
    # while read_count != READ_TIMEOUT:
    # for cnt in range(READ_TIMEOUT):
    #     TCTemperature2 = read_thermocouple(BoardPos, tspi)
    tspi.deinit()



def verify_sensor(BoardPos, TCId, RefTemp):
    if TCId in conf.callibrations:
        print(f'For board position {BoardPos}')
        print(f'Thermocouple ID was found with value: {TCId}\n')
        print(f'Equation: y = b0 + b1x + b2x^2')
        print(f'b0 = {conf.callibrations[TCId][1]}')
        print(f'b1 = {conf.callibrations[TCId][2]}')
        print(f'b2 = {conf.callibrations[TCId][3]}')
        print('\n')
        return True
    else:
        print("Thermocouple was not found.\n")
        return False

while True:
    print("Type 'exit' to stop:")
    BoardPos = input("Enter board position (1-5):")
    if 'exit' == BoardPos:
        break
    TCId = input('Enter thermocouple id ("101", "T2", etc.):')
    RefTemp = input("Enter reference temperature in celsius (0.00):")
    # convert string values into clean values and correct types
    BoardPos = BoardPos.strip()
    TCId = TCId.strip()
    RefTemp = float(RefTemp)
    # only try to callibrate if the sensor entry already exists in the conf.py file
    if verify_sensor(BoardPos, TCId, RefTemp):
        print("Hold thermocouple steady at reference and wait for confirmation or Failed message.")
        print("Callibrating...")
        callibrate(BoardPos, TCId)
    else:
        print(f"Sensor ID {TCId} was not found.\n")

print("Done")
