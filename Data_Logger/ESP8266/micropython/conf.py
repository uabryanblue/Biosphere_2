"""
 place all configuration constants in this file
 this file can be uploaded and then system reset
 """

AUTHOR = "Bryan Blue - bryanblue@arizona.edu"
VERSION = "23.0.0"

# DEVICE IDENTIFICATION
MYID = "2"
MYNAME = "ESP8266 MicroPython Temperature Server"


"""NETWORK CONFIGURATION"""
# --HOME--
# WAP_SSID = "DEA_VAN3"
# WAP_PSWD = "Help1Sago8!MoMo"
# unit 1 use port 666
# unit 2 use port 667
# PORT = 667

# --BIOSPHERE 2--
# publice IP: 150.135.165.93
WAP_SSID = "b2science"
WAP_PSWD = ""
PORT = 80

# --test direct--
# WAP_SSID = "MicroPython-e37cfc"
# WAP_PSWD = "micropythoN"
# PORT = 80

# TIMESERVER
NTP_HOST = """3.netbsd.pool.ntp.org"""
UTC_OFFSET = -7 * 60 * 60  # -7 arizona time


# DATABASE
# this should be the base url up to, but not including, the "?" character
# DB_URL = """http://www.theexternet.com/printing.php"""  # 200 okay test URL
# DB_URL = """https://adwriter.com/privacy-policy.php""" # 301 permanent move URL
DB_URL = """https://lazuline.us/mypage"""  # 404 not found error
# DB_URL = """http://biosphere2.000webhostapp.com/dbwrite.php"""  # intitial test DB location

# LOOGER
LOG_MOUNT = "log"
LOG_FILENAME = "logger.dat"
