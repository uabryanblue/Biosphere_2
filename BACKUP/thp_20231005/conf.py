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
# MYROLE = "TRCCONTROL" # multiple thermocouple sensor with relay box
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
peers["DATA_LOGGER"] = [b'\xc4[\xbe\xe4\xfe\x08', b'\x8c\xaa\xb5M\x7f\x18', b'HU\x19\xdf)\x86']  # list of data loggers
# one entry from DATA_LOGGER needs to be sent as TIME
# TODO change to look at the DATA_LOGGER entries as they all can send the time
peers["TIME"] = [b'\xc4[\xbe\xe4\xfe\x08'] # try to get time from here
# --------------------

# --------------------
# SENSOR READINGS
# AVG_INTERVAL - number of minutes used to calculate and send an average
AVG_INTERVAL = 15