"""
 place all configuration constants in this file
 this file can be uploaded and then the system reset
 """

AUTHOR = "Bryan Blue - bryanblue@arizona.edu"
VERSION = "25.90.0"

#----------------------
# DEVICE ROLE
# uncomment one of the corresponding lines to change how
# the code executes. The different configurations are shown here
# MYROLE = "CALIBRATE" # command line callibration
# MYROLE = "DATALOGGER" # data logger box
MYROLE = "TRC" # multiple thermocouple sensor with relay box
# MYROLE = "THP" # temperatue humidity pressure aspirated sensor

# --------------------
# DEVICE IDENTIFICATION
# Communication identification is done using the MAC address of the ESP8266
# MYID = "2" # this is a short id and should not be used unless you know what you are doing
MYNAME = "ESP8266 MicroPython Temperature Sensor and Temperature Control" # long generic description
# --------------------

# --------------------
# WiFi NETWORK CONFIGURATION
# do not use with ESPNow

# --test direct--
# WAP_SSID = "MicroPython-e37cfc"
# WAP_PSWD = "micropythoN"
# PORT = 80
# --------------------

# --------------------
# ESPNow CONFIGURATION
# peers are binary MAC addresses to send to
# up to 4 can be specified
# peers is a dict that points to a list
# these are initialized with the ESPNow add_peer()
# All of these Values need to be contained in the DATA_LOOGER entry
#   for the others to work
# Values:
#   DATA_LOGGER - send readings to these MAC addresses in binary format
#   TIME - get date/time from this device, should only be ONE entry
#   REMOTE - data logger to register remote sensors
#   CALIBRATE - data logger to store calibration data
peers = {}
# remote sensor configuration, connect to all data loggers, pick one for time
peers["DATA_LOGGER"] = [b'\xc4[\xbe\xe4\xfe\x08', b'\x8c\xaa\xb5M\x7f\x18', b'HU\x19\xdf)\x86', b'\xc4[\xbe\xe5\x03R']  # list of data loggers
peers["TIME"] = [b'HU\x19\xdf)\x86'] # try to get time from here M1
# peers["TIME"] = [b'\xc4[\xbe\xe4\xfe\x08'] # TEST BENCH!!!!!!!  M7

# --------------------
# DATA LOGGER
# these are configuration locaions for a mount and filename
# on a MicroSD card. Max Card Size: 32 GB
# LOG_MOUNT = "//log" # must start with "//" the root folder
# CAL_FILENAME = "callibration.dat"
# LOG_FILENAME = "logger.dat" # no leading / depricated
# SYSTEM_LOG = "sys.log" # no leading / depricated
# --------------------

# --------------------
# HEAING VALUES
# --------------------
# desired degrees celsius differential of warmed leaf vs control leaf
TDIFF = 3 # number of degees, not a temperature e.g. 3 degrees C above ambient

# maxiumum celsius temperature of heated leaf
# this is the highest value that heating should be applied
# it is a failsafe to prevent scorching, or in case of heater malfunction
# to cut the power
# Value must be less than TMAX_HEATER
TMAX = 52 # 122 F

# maximum degrees celsius that the heating device should achieve
# this will turn the device off at this setpoint and should be
# considered a maximum constraint of the heating device
# safety value, shut the power off
# Value must be greater than TMAX !!!
TMAX_HEATER = 55 # 140 F

# --------------------
# SENSOR READINGS
# --------------------
# !!!!!!!! LOG_INTERVAl MUST BE GREATER THAN SAMPLE_INTERVAL !!!!!!!
# LOG_INTERVAL (float) in minutes
# SAMPLE_INTERVAL (float) in ms e.g. take a sample every 15 seconds = 15000 ms
# TC_READS (int) number of TC reads averaged together to make 1 sample value
LOG_INTERVAL = 3 # minutes, larger than SAMPLE_INTERVAL
SAMPLE_INTERVAL = 5000 # ms
TC_READS = 4

# --------------------
# 5 THERMOCOUPLE CONFIGURATIONS
# --------------------
# assign temperature sensors D0 - D4 locations to a data structure
# first list element: D0 - D4 correspond to the physical pins on the ESP8266
# second list element: GPIO number corresponding to D0 - D4
# third list element: temperature value
# sensor readings are recorded in a dictionary containing lists
readings = {}
# requres 1 of each value:
#   HEAT - heating device temperature
#   CONTROL - control leaf temperature
#   REFERENCE - reference leaf temperature
#   TREATMENT - heated leaf temperature
#   CONTROL_HEAT - control heating pad temperature, not on or heating
#   Define each dictionary element as a PIN, GPIO, TempValue, SensorID, 0.0
# EXAMPLE:  readings['TREATMENT'] = [1, 16, 0.0, 101, 0.0]
# key = HEATER, PIN = D0 (T1 port), GPIO 16, initial temp value = 0.0
# SensorID = a unique ID used for identification of the thermocouple in that position
#    this may not longer be needed
# Internal Temperature - cold junction on the amplifier board
readings['TREATMENT'] = [1, 16, 0.0, 101, 0.0]
readings['CONTROL'] = [2, 5, 0.0, 119, 0.0]
readings['REFERENCE'] = [3, 4, 0.0, 103, 0.0]
readings['HEAT'] = [4, 0, 0.0, 104, 0.0]
readings['CONTROL_HEAT'] = [5, 2, 0.0, 105, 0.0]

# OUTPUT ORDER
# this controls the 5 temperature sensor readings' output order
# output will be a CSV with values corresponding to this order
# readingsOrder = ['TREATMENT', 'CONTROL', 'HEATER', 'D3', 'D4']
# the values are the "key" values from the readings[key] = []
readingsOrder = ['TREATMENT', 'CONTROL', 'REFERENCE', 'HEAT', 'CONTROL_HEAT']

# CALLIBRATION TABLE
# Each thermocouple must be callibrated
# key - one of 5 values from readings{} e.g. "TREATMENT"
# A unique value for the ID
# the callibration coefficients need to be supplied
# When taking a temperature reading, if an entry is not found, no adjustment will be applied
    # Position = 1 through 5 is the corresponding port on the board
    # beta0 = -15.35578 - offset
    # beta1 = 1.90714 - slope (beta1 * X)
    # beta2 = -0.01053 - 2nd order (beta2 * X^2 ), if needed, set to 0 for linear
callibrations = {}
# # EXAMPLES ONLY !!!!! these values are not correct

## CALIBRATION THERMOCOUPLE SENSOR TABLE
# this is a GLOBAL config - do NOT modify unless you know what you are doing
# assign KEY values to the TC you are using in your installation
# comment out the lines for those not in use
#  = [NAME, PORT, INTERCEPT, SLOPE, QUADRATIC (normally 0)]
# to get values without a calibration use this form\
#  = [NAME, PORT, 0, 1, 0] 

# BAD T116, T111, T110

# TC Configuration 1
callibrations['TREATMENT'] =        ["T103", 1, -2.5112, 1.0223, 0] 
callibrations['CONTROL'] =          ["T105", 2, -3.6912, 1.0107, 0]
callibrations['REFERENCE'] =        ["T109", 3, -4.1935, 1.0625, 0] 
callibrations['HEAT'] =             ["T118", 4, -3.6352, 1.0157, 0]
callibrations['CONTROL_HEAT'] =     ["T107", 5, -3.7182, 1.0541, 0] 

# TC Configuration 2
# callibrations['TREATMENT'] =        ["T115", 1, -1.9282, 1.0463, 0] 
# callibrations['CONTROL'] =          ["T112", 2, -5.574, 1.1665, 0]
# callibrations['REFERENCE'] =        ["T104", 3, -2.2076, 1.0349, 0] 
# callibrations['HEAT'] =             ["T106", 4, -3.9144, 1.1191, 0]
# callibrations['CONTROL_HEAT'] =     ["T113", 5, -3.496, 1.1118, 0] 

# # TC Configuration 3
# callibrations['TREATMENT'] =        ["T119", 1, 0, 1, 0] 
# callibrations['CONTROL'] =          ["T121", 2, 0, 1, 0]
# callibrations['REFERENCE'] =        ["T117", 3, 0, 1, 0] 
# callibrations['HEAT'] =             ["T102", 4, 0, 1, 0]
# callibrations['CONTROL_HEAT'] =     ["T101", 5, 0, 1, 0] 