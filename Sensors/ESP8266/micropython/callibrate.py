import conf
import thermocouple
import logger
import sys


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
def callibrate(BoardPos, TCId, RefTemp):
    if TCId in conf.callibrations:
        print(f'For board position {BoardPos}')
        print(f'Thermocouple ID was found with value: {TCId}\n')
        print(f'Equation: y = b0 + b1x + b2x^2')
        print(f'b0 = {conf.callibrations[TCId][1]}')
        print(f'b1 = {conf.callibrations[TCId][2]}')
        print(f'b2 = {conf.callibrations[TCId][3]}')
        print('\n')
    else:
        print("Thermocouple was not found.\n")

def validate_input(input):
        clean_data = input.strip()
        print(f' cleaned data ***{clean_data}***')

while True:
    print("Enter callibration information as follows, type 'Exit' to stop:")
    print("BoardPosition, ThermocoupleID, ActualTemperature")
    BoardPos = input("Enter board position (1-5):")
    if 'Exit' == BoardPos:
        break
    TCId = input("Enter thermocouple id (0-999):")
    RefTemp = input("Enter reference temperature in celsius:")
    print("Hold thermocouple steady at reference and wait for confirmation or Failed message.")
    print("Callibrating...")
    callibrate(BoardPos, TCId, RefTemp)


    # data = input("Please enter the message:\n")

    # print(f'Processing Message from input() *****{data}*****')
    # validate_input(data)
print("Done")
