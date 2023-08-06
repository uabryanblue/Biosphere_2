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
import gc
# import logger

import time
import sys
import machine
import math

NUM_READINGS = 30  # the number of consecutive readings that must fall within VARIANCE
VARIANCE = 0.1  # how small variance of NUM_READINGS values must be before accepting reading
READ_TIMEOUT = 50  # number of readings to take before failing to calibrate


# THIS IS WRONG!!!
def variance(lst):

    if len(lst) > 0 and len(lst) > 0:
        avg = sum(lst) / len(lst)
        var = sum(abs((x - avg)) ** 2 for x in lst) / len(lst)  # sample variance
        return var
    else:
        return float("NaN")

# sample = 1 => sample std
# sample = 0 => population std
def stddev(data, sample = 1):
    if sample != 0 and sample != 1:
        return 0.0
    # Number of observations
    n = len(data)
    # Mean of the data
    mean = sum(data) / n - sample
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
    # print(f"Taking temperature readings from board sensor position {BoardPos}")
    while (read_count < READ_TIMEOUT) and (TVar > VARIANCE):
        temperature, internalTemp = thermocouple.read_thermocouple(BoardPos, tspi)
        if not math.isnan(temperature):
            while len(TRead) > NUM_READINGS:
                del TRead[0]  # remove first element so next added to end
            TRead.append(temperature)
        else:
            print(
                f"ERROR !!!!! NaN reading given, check the connection on board position {BoardPos} and try again."
            )
            tspi.deinit()
            return float("NaN"), float("NaN")
        read_count += 1
        if read_count >= NUM_READINGS:
            TVar = variance(TRead)
        # print(f"{TRead} var {TVar}")
        time.sleep(0.25)
    print(
        f"Total number of readings taken: {read_count}"
    )
    tspi.deinit()
    TAvg = sum(TRead) / len(TRead)

    # return the list, avarage and variance
    return TRead, TAvg, TVar


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


def calibrate_main(esp_con, station, RAW_MAC):
    while True:
        gc.collect()

        print("Press Enter to continue.")
        BoardPos = input()
        BoardPos = input("Enter board position 1 to 5 (1 default) or 'exit' ot quit:") 
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
            # print(f"Callibrating sensor on board position {BoardPos}...\n")
            TCList, TCAvg, TCVar = calibrate(BoardPos, TCId)
            print("\n================== RESULTS ==================")
            range = max(TCList) - min(TCList)
            print(f"FINAL VALUES: {TCList}")
            print(f"RANGE: {range:<20}") # TODO change the formatting, this is wrong
            print(f"AVERAGE: {TCAvg:<20}")
            # print(f"VARIANCE: {TCVar}")
            std = stddev(TCList, 1) # 1 - sample
            print(f"STD DEVIATION: {std:<20}")
            print(f"CV: {std/TCAvg:<20}")
            print("=============================================")
            print("\n")
            if TCVar > VARIANCE:
                print(
                    f"CALLIBRATION FAILED!!! Final variance greater than {VARIANCE} at {TCVar}"
                )
        else:
            print(f"Sensor ID {TCId} was not found.\n")
