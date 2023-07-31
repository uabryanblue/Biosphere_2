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

import time
import sys
import machine
import math

NUM_READINGS = 10  # the number of consecutive readings that must fall within VARIANCE
VARIANCE = (
    0.1  # how small variance of NUM_READINGS values must be before accepting reading
)
READ_TIMEOUT = 50  # number of readings to take before failing to calibrate


def variance(lst):

    if len(lst) > 0 and len(lst) > 0:
        avg = sum(lst) / len(lst)
        var = sum(abs((x - avg)) ** 2 for x in lst) / len(lst)  # sample variance
        return var
    else:
        return float("NaN")

def popstddev(data):
    # Number of observations
    n = len(data)
    # Mean of the data
    mean = sum(data) / n
    # Square deviations
    deviations = [(x - mean) ** 2 for x in data]
    # stddev
    stddev = math.sqrt(sum(deviations) / (n))
    return stddev


def calibrate(BoardPos, TCId):
    read_count = 0
    TRead = []
    TVar = 100.0
    tspi = machine.SPI(1, baudrate=5000000, polarity=0, phase=0)
    # print(tspi)
    # read the first NUM_READINGS to calculate variance
    print(f"Taking temperature readings from board sensor position {BoardPos}")
    while (read_count < READ_TIMEOUT) and (TVar > VARIANCE):
        temperature, internalTemp = thermocouple.read_thermocouple(BoardPos, tspi)
        if not math.isnan(temperature):
            while len(TRead) > NUM_READINGS:
                del TRead[0]  # remove first element so next added to end
            TRead.append(temperature)
        else:
            print(
                f"NaN reading given, check your connections on board position {BoardPos} and try again."
            )
            tspi.deinit()
            return float("NaN"), float("NaN")
        read_count += 1
        if read_count >= NUM_READINGS:
            TVar = variance(TRead)
        print(f"{TRead} var {TVar}")
        time.sleep(1)
    print(
        f"Total number of readings taken: {read_count} the last {NUM_READINGS} with values of {TRead}"
    )
    # TVar = variance(TRead)
    # print(f"varince of readings: {TVar}")
    tspi.deinit()
    # return the list, avarage and variance
    return TRead, sum(TRead) / len(TRead), TVar


def verify_sensor(BoardPos, TCId, RefTemp):
    if TCId in conf.callibrations:
        print(f"For board position {BoardPos}")
        print(f"Thermocouple ID was found with value: {TCId}\n")
        print(f"Equation: y = b0 + b1x + b2x^2")
        print(f"b0 = {conf.callibrations[TCId][1]}")
        print(f"b1 = {conf.callibrations[TCId][2]}")
        print(f"b2 = {conf.callibrations[TCId][3]}")
        print("\n")
        return True
    else:
        print("Thermocouple was not found.\n")
        return False


def calibrate_main():
    while True:
        print("Type 'exit' to stop:")
        BoardPos = input()
        BoardPos = input("Enter board position 1 to 5 (1 default):") # TODO this is not working on first pass
        # BoardPos = "1"
        print(f"BoardPos debug |{BoardPos}|")
        if "exit" == BoardPos:
            break
        BoardPos = int(BoardPos)
        if not BoardPos or BoardPos < 1 or BoardPos > 5:
            BoardPos = "1"
        TCId = input('Enter thermocouple id ("101", "T2", etc.):')
        TCId = TCId.strip()
        RefTemp = input("Enter reference temperature in celsius (0.00):")
        RefTemp = float(RefTemp)
        # only try to calibrate if the sensor entry already exists in the conf.py file
        if verify_sensor(BoardPos, TCId, RefTemp):
            print(
                "Hold thermocouple steady at reference and wait for confirmation or Failed message."
            )
            print("Callibrating...")
            TCList, TCAvg, TCVar = calibrate(BoardPos, TCId)
            range = max(TCList) - min(TCList)
            print(f"FINAL VALUES: {TCList}")
            print(f"RANGE: {range}")
            print(f"AVERAGE: {TCAvg}")
            print(f"VARIANCE: {TCVar}")
            std = popstddev(TCList)
            print(f"STD DEVIATION: {std}")
            print(f"CV: {std/TCAvg}")
            print("\n")
            if TCVar > VARIANCE:
                print(
                    f"CALLIBRATION FAILED!!! Final variance greater than {VARIANCE} at {TCVar}"
                )
        else:
            print(f"Sensor ID {TCId} was not found.\n")
