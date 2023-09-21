"""
 place all configuration constants in this file
 this file can be uploaded and then the system reset
 """

AUTHOR = "Bryan Blue - bryanblue@arizona.edu"
VERSION = "25.1.1"

#----------------------
# DEVICE ROLE
# uncomment one of the corresponding lines to change how
# the code executes. The different configurations are shown here
# MYROLE = "CALIBRATE" # command line callibration
MYROLE = "THP" # data logger box
# MYROLE = "TRCCONTROL" # multiple thermocouple sensor with relay box
# MYROLE = "THP" # temperatue humidity pressure aspirated sensor

# --------------------
# DEVICE IDENTIFICATION
# Communication identification is done using the MAC address of the ESP8266
# MYID = "2" # this is a short id and should not be used unless you know what you are doing
MYNAME = "ESP8266 MicroPython Temperature Humidity Pressure Sensor" # long generic description
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

# # --------------------
# # DATA LOGGER
# # these are configuration locaions for a mount and filename
# # on a MicroSD card. Max Card Size: 32 GB
# LOG_MOUNT = "//log" # must start with "//" the root folder
# CAL_FILENAME = "callibration.dat"
# LOG_FILENAME = "logger.dat" # no leading /
# SYSTEM_LOG = "sys.log" # no leading /
# # --------------------
