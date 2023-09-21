"""
 place all configuration constants in this file
 this file can be uploaded and then the system reset
 """

AUTHOR = "Bryan Blue - bryanblue@arizona.edu"
VERSION = "25.1.1"

#----------------------
# DEVICE ROLE
MYROLE = "THP" # data logger box

# --------------------
# DEVICE IDENTIFICATION
# Communication identification is done using the MAC address of the ESP8266
# MYID = "2" # this is a short id and should not be used unless you know what you are doing
MYNAME = "ESP8266 MicroPython Temperature Humidity Pressure Sensor" # long generic description
# --------------------

# --------------------
# ESPNow CONFIGURATION
# peers are binary MAC addresses to send to
# up to 4 can be specified
# peers is a dict that points to a list
# these are initialized with the ESPNow add_peer()
# Values:
#   DATA_LOGGER - send readings to these MAC addresses in binary format
#   TIME - get date/time from this device, should only be ONE entry
#   REMOTE - data logger to register remote sensors
# EXAMPLE: peers["DATA_LOGGER"] = [b'\xc4[\xbe\xe4\xfe=']
peers = {}
# remote sensor configuration, connect to all data loggers, pick one for time
peers["DATA_LOGGER"] = [b'\xc4[\xbe\xe4\xfe\x08', b'\x8c\xaa\xb5M\x7f\x18']  # kist of data loggers
peers["TIME"] = [b'\x8c\xaa\xb5M\x7f\x18'] # try to get time from here
# data logger information
peers["REMOTE"] = [b'\xc4[\xbe\xe4\xfdq'] # TRC testing 20230731
# --------------------

# --------------------
# SENSOR READINGS
# AVG_INTERVAL - number of minutes used to calculate and send an average
AVG_INTERVAL = 5
