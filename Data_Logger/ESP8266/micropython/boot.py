"""
Biosphere 2 remote sensing project
AUTHOR: Bryan Blue
EMAIL: bryanblue@arizona.edu
STARTED: 2023
"""

import gc
# import time
import esp
import conf
# from machine import Pin
import realtc
import sd
import sys
from time import sleep
# import espnowex
import uerrno  # error trapping and code values

esp.osdebug(None)


# pushes first real line of output
# to the line after the terminal garbage finishes
# "garbage" is due to mismatch in terminal speed on boot, not a bug
print("booting")

# set the on board RTC to the time from the DS3231
realtc.rtcinit()
print("set time")

# attach SD card module and mount the SD card, if one is present
# TODO error trapping and what to do if there isn't one to use?
# mnt = '/' + conf.LOG_MOUNT
# print(f"unmount: {mnt}")
# sd.closeSD(mnt)
# print(f"mount: {mnt}")
# try:
#     sd.initSD(mnt)
# except OSError as e:
#     print(f"OSError: Connection closed {e}")
#     sys.exit(0)

# sleep(0.5)