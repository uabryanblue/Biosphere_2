"""
Biosphere 2 remote sensing project
AUTHOR: Bryan Blue
EMAIL: bryanblue@arizona.edu
STARTED: 2023
"""

import esp
import realtc

esp.osdebug(None)

# pushes first real line of output
# to the line after the terminal garbage finishes
# "garbage" is due to mismatch in terminal speed on boot, not a bug
print("booting")

# set the on board RTC to the time from the DS3231
realtc.rtcinit()
print("set time")
