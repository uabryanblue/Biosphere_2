"""
Biosphere 2 remote sensing project
AUTHOR: Bryan Blue
EMAIL: bryanblue@arizona.edu
STARTED: 2023
"""

import esp
import gc
# from realtc import rtcsetup
# decrease space used by esp system logging
esp.osdebug(None)
gc.enable()
gc.collect()
# rtcsetup()
# pushes first real line of output
# to the line after the terminal garbage finishes
# "garbage" is due to mismatch in terminal speed on boot, not a bug
print("booting")
