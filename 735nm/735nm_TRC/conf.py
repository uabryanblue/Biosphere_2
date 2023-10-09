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
MYROLE = "TRCCONTROL" # multiple thermocouple sensor with relay box
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
# --BIOSPHERE 2 WiFi Atmospheric Lab--
# publice IP: 150.135.165.93
# WAP_SSID = "b2science"
# WAP_PSWD = ""
# PORT = 80

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
peers["DATA_LOGGER"] = [b'\xc4[\xbe\xe4\xfe\x08', b'\x8c\xaa\xb5M\x7f\x18', b'HU\x19\xdf)\x86']  # list of data loggers
# peers["TIME"] = [b'\xc4[\xbe\xe4\xfe\x08'] # try to get time from here
peers["TIME"] = [b'HU\x19\xdf)\x86'] # try to get time from M1

# --------------------
# SENSOR READINGS
# AVG_INTERVAL - number of minutes used to calculate and send an average
# AVG_INTERVAL = 5

# --------------------
# DATA LOGGER
# these are configuration locaions for a mount and filename
# on a MicroSD card. Max Card Size: 32 GB
LOG_MOUNT = "//log" # must start with "//" the root folder
CAL_FILENAME = "callibration.dat"
LOG_FILENAME = "logger.dat" # no leading / depricated
SYSTEM_LOG = "sys.log" # no leading / depricated
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
TMAX = 50 # 122 F

# maximum degrees celsius that the heating device should achieve
# this will turn the device off at this setpoint and should be
# considered a maximum constraint of the heating device
# safety value, shut the power off
# Value must be greater than TMAX !!!
TMAX_HEATER = 60 # 140 F

# delay in seconds between consecutive readings
TREAD_INTERVAL = 15

# assign temperature sensors D0 - D4 locations to a data structure
# first list element: D0 - D4 correspond to the physical pins on the ESP8266
# second list element: GPIO number corresponding to D0 - D4
# third list element: temperature value
# sensor readings are recorded in a dictionary containing lists
readings = {}
# requres 1 of each value:
#   HEATER - heating device temperature
#   CONTROL - control leaf temperature
#   TREATMENT - leaf that is being heated
#   D3, D4 - 2 extra sensors
#   Define each dictionary element as a PIN, GPIO, TempValue, SensorID, 0.0
# EXAMPLE:  readings['HEATER'] = [1, 16, 0.0, 101, 0.0]
# key = HEATER, PIN = D0, GPIO 16, initial temp value = 0.0
# SensorID = a unique ID used for identification of the thermocouple in that position
# Internal Temperature - cold junction on the amplifier board
#   See CALLIBRATION below
readings['HEATER'] = [1, 16, 0.0, 101, 0.0]
readings['CONTROL'] = [2, 5, 0.0, 102, 0.0]
readings['TREATMENT'] = [3, 4, 0.0, 103, 0.0]
# two extra sensor locations, default D3 and D4
readings['D3'] = [4, 0, 0.0, 104, 0.0]
readings['D4'] = [5, 2, 0.0, 105, 0.0]

# OUTPUT ORDER
# this controls the 5 temperature sensor readings' output order
# output will be a CSV with values corresponding to this order
# readingsOrder = ['TREATMENT', 'CONTROL', 'HEATER', 'D3', 'D4']
# the values are the "key" values from the readings[key] = []
readingsOrder = ['HEATER', 'CONTROL', 'TREATMENT', 'D3', 'D4']

# CALLIBRATION TABLE
# Each thermocouple must be callibrated
# A unique value for the ID, and the callibration coefficients need to be supplied
# When taking a temperature reading, if an entry is not found, no adjustment will be applied
    # Position = 1 through 5 denoting it was callibrated in this position of the board
    # beta0 = -15.35578 - offset
    # beta1 = 1.90714 - slope
    # beta2 = -0.01053 - 2nd order, if needed, set to 0 for linear
callibrations = {}
# EXAMPLES ONLY !!!!! these values are not correct
callibrations['101'] = [1, 28.5, 0.262, 0]
callibrations['102'] = [2, 98.5, 4.20, 0]
callibrations['103'] = [3, 22.9, -0.0542, 0]
callibrations['104'] = [4, -14.1, -2.14, 0]
callibrations['105'] = [5, 21.3, -0.148, 0]
