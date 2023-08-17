""" 
AUTHOR: Bryan Blue, bryanblue@arizona.edu
For edcuational use only. Not to be used commercially or sold without permission
of the AUTHOR.

    This script is for interactive callibration of thermocouples
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

import espnowex
import time
import sys
import machine
import math

NUM_READINGS = 30  # the number of consecutive readings that must fall within VARIANCE
# STDVAL = 1.05 # how far each value is from the mean
RANGE = 0.75 # how far min and max values of 30 points need to be to pass
READ_TIMEOUT = 50  # number of readings to take before failing to calibrate


def stddev(data, sample = 1):
    """ sample = 1 => sample std (default)
        sample = 0 => population std """

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
    """ take NUM_READINGS consecutive readings until the number of values
        get to the READ_TIMEOUT value or the desired error is met """
        
    read_count = 0
    TRead = []
    TVar = 100.0
    std = 100.0 # arbitrary bad range
    rng = 3 # degrees difference in 30 values
    tspi = machine.SPI(1, baudrate=5000000, polarity=0, phase=0)

    while (read_count < READ_TIMEOUT) and (rng > RANGE):
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
            rng = max(TRead) - min(TRead)
        time.sleep(0.25)
    print(
        f"Total number of readings taken: {read_count}"
    )
    tspi.deinit()

    return TRead

def calibrate_main(esp_con, station, RAW_MAC):
    while True:
        gc.collect()
        MY_MAC = ":".join(["{:02x}".format(b) for b in RAW_MAC]).upper()

        # BoardPos is the physical TC position on circuit board T1 - T5
        BoardPos = input("Press Enter to continue ('q' to quit): ")
        if BoardPos.upper() == 'Q':
            break
        while BoardPos not in ['1','2','3','4','5']:
            BoardPos = input("Enter board position 1 to 5:")
        BoardPos = int(BoardPos)

        # user value can be whatever they want but not blank
        TCId = input('Enter thermocouple ID ("101", "T2", etc.): ')
        while len(TCId.strip()) == 0:
            TCId = input('ID cannot be empty.\nEnter thermocouple ID ("101", "T2", etc.):' )
        TCId = TCId.strip()

        # a temperature can only be numberic, period, or a sign
        RefTemp = input("Enter reference temperature in celsius (0.00): ")
        while not bool(RefTemp and not RefTemp.strip("0123456789.-+")):
            RefTemp = input("Value must be a float.\nEnter reference temperature in celsius (0.00): ")
        RefTemp = float(RefTemp)

        print(
            "\nHold thermocouple steady at reference and wait for confirmation or Failed message."
        )

        TCList = calibrate(BoardPos, TCId)
        gc.collect()
        print("\n================== RESULTS ==================")
        range = max(TCList) - min(TCList) # range is used for control of accepting readings
        TCAvg = sum(TCList) / len(TCList) # 30 sample average
        std = stddev(TCList, 1) # 1 - sample std
        print(f"VALUES: {TCList}")
        print(f"MIN, MAX: {min(TCList)}, {max(TCList)}")
        print(f"RANGE: {range}")
        print(f"MEAN: {TCAvg:<20}")
        print(f"STD DEVIATION: {std:<20}") # number of degrees from the mean each point falls into
        # on average, each value deviates from the mean by std degrees 
        print(f"CV: {std/TCAvg:<20}")
        print("=============================================")
        print("\n")

        if range > RANGE:
            print(
                f"CALLIBRATION FAILED!!! Out of specified range of {RANGE} at {range}"
            )
        else:
            record_value = input("Enter 'r' to record calibration value (any other key to skip): ")
            if record_value.upper() == 'R':    
                #  send information to datalogger, data must start with "CALIBRATE:"
                #  date/time added at data logger
                data = ','.join(str(out) for out in [MY_MAC, TCId, BoardPos, RefTemp, str(TCList)])
                data = f"CALIBRATE:{data.replace(' ','')}" # get rid of all spaces to keep under 250 byte max
                print(data)
                gc.collect()
                # send the data to every conf entry in CALIBRATE
                [espnowex.esp_tx(val, esp_con, data) for val in conf.peers['CALIBRATE']]
                print("\nCALIBRATION READINGS SENT TO DATA LOGGER.\n")
            else:
                print('\nCALIBRATION READINGS NOT RECORDED!\n')
            gc.collect()

