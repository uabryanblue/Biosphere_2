"""
 place all configuration constants in this file
 this file can be uploaded and then the system reset
 """

AUTHOR = "Bryan Blue - bryanblue@arizona.edu"
VERSION = "25.1.1"

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
# TIMESERVER
# NTP_HOST = """3.netbsd.pool.ntp.org"""
# UTC_OFFSET = -7 * 60 * 60  # -7 arizona time
# --------------------

# --------------------
# DATABASE - NOT USED!!!
# this should be the base url up to, but not including, the "?" character
DB_URL = """http://biosphere2.000webhostapp.com/dbwrite.php"""  # intitial test DB location
# --------------------

# --------------------
# DATA LOGGER
# these are configuration locaions for a mount and filename
# on a MicroSD card. Max Card Size: 32 GB
LOG_MOUNT = "/log"
LOG_FILENAME = "sensor_log.dat"
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

# assign temperature sensors D0 - D4 locations to a data structure
# first list element: D0 - D4 correspond to the physical pins on the ESP8266
# second list element: GPIO number corresponding to D0 - D4
# third list element: temperature value
# sensor readings are recorded in a dictionary containing lists
readings = dict()
# requres 1 of each value:
# HEATER - heating device temperature
# CONTROL - control leaf temperature
# TREATMENT - leaf that is being heated
# D3, D4 - 2 extra sensors
# Define each dictionary element as a PIN, GPIO, TempValue
# EXAMPLE:  readings['HEATER'] = [1, 16, 0.0]
# key = HEATER, PIN = D0, GPIO 16, initial temp value = 0.0
# SensorID = a unique ID used for identification of the thermocouple in that position
#   See CALLIBRATION below
readings['HEATER'] = [1, 16, 0.0, 101]
readings['CONTROL'] = [2, 5, 0.0, 102]
readings['TREATMENT'] = [3, 4, 0.0, 103]
# two extra sensor locations, default D3 and D4
readings['D3'] = [4, 0, 0.0, 104]
readings['D4'] = [5, 2, 0.0, 105]

# Output Order
# this controls the 5 temperature sensor readings' output order
# output will be a CSV with values corresponding to this order
readingsOrder = ['TREATMENT', 'CONTROL', 'HEATER', 'D3', 'D4']

# CALLIBRATION TABLE
# Each thermocouple must be callibrated
# A unique value for the ID, and the callibration coefficients need to be supplied
# When taking a temperature reading, if an entry is not found, no adjustment will be applied
    # Position = 1 through 5 denoting it was callibrated in this position of the board
    # beta0 = -15.35578 - offset
    # beta1 = 1.90714 - slope
    # beta2 = -0.01053 - 2nd order, if needed, set to 0 for linear
callibrations = dict()
# TODO these values are not correct
callibrations[101] = [1, 28.5, 0.262, 0]
callibrations[102] = [2, 98.5, 4.20, 0]
callibrations[103] = [3, 22.9, -0.0542, 0]
callibrations[104] = [4, -14.1, -2.14, 0]
callibrations[105] = [5, 21.3, -0.148, 0]
