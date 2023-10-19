"""
 place all configuration constants in this file
 this file can be uploaded and then the system reset
 """

AUTHOR = "Bryan Blue - bryanblue@arizona.edu"
VERSION = "25.3.1"

# --------------------
# DEVICE IDENTIFICATION
MYNAME = "ESP8266 MicroPython Temperature, Humidity, Pressure Sensor" # long generic description
# --------------------

#----------------------
# DEVICE ROLE
# uncomment one of the corresponding lines to change how
# the code executes. The different configurations are shown here
# MYROLE = "CALIBRATE" # command line callibration
# MYROLE = "DATALOGGER" # data logger box
# MYROLE = "TRC" # multiple thermocouple sensor with relay box
MYROLE = "THP" # temperatue humidity pressure aspirated sensor

# --------------------
# ESPNow CONFIGURATION
# peers are binary MAC addresses to send to
# peers is a dict that points to a list
# these are initialized with the ESPNow add_peer()
# Values:
#   DATA_LOGGER - send readings to these MAC addresses in binary format
#   TIME - get date/time from this device, should only be ONE entry
# EXAMPLE: peers["DATA_LOGGER"] = [b'\xc4[\xbe\xe4\xfe=']
peers = {}
# remote sensor configuration, connect to all data loggers, pick one for time
# peers["DATA_LOGGER"] = [b'\xc4[\xbe\xe4\xfe\x08', b'\x8c\xaa\xb5M\x7f\x18', b'HU\x19\xdf)\x86', b'\xc4[\xbe\xe5\x03R']  # list of data loggers
peers["DATA_LOGGER"] = [b'\xc4[\xbe\xe4\xfe\x08', b'\x8c\xaa\xb5M\x7f\x18', b'HU\x19\xdf)\x86', b'\xc4[\xbe\xe5\x03R']  # list of data loggers
# one entry from DATA_LOGGER needs to be sent as TIME
# TODO change to look at the DATA_LOGGER entries as they all can send the time
# peers["TIME"] = [b'\xc4[\xbe\xe5\x03R'] # try to get time from here
# peers["TIME"] = [b'\xc4[\xbe\xe4\xfe\x08'] # try to get time from here
peers["TIME"] = [b'\xc4[\xbe\xe4\xfe\x08'] # try to get time from here M1

# --------------------

# --------------------
# SENSOR READINGS
# !!!!!!!! LOG_INTERVAl MUST BE GREATER THAN SAMPLE_INTERVAL !!!!!!!
# LOG_INTERVAL in minutes
# SAMPLE_INTERVAL in ms e.g. 15 seconds = 15000 ms
LOG_INTERVAL = 15 # minutes, larger than SAMPLE_INTERVAL
SAMPLE_INTERVAL = 15000 # ms