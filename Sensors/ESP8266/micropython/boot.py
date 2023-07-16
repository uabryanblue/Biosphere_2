"""
Biosphere 2 remote sensing project
AUTHOR: Bryan Blue
EMAIL: bryanblue@arizona.edu
STARTED: 2023
"""

# import gc
# import time
import esp
# import conf
# from machine import Pin
# import realtc
# import sd
# from time import sleep
# import espnowex

# decrease space used by esp system logging
esp.osdebug(None)


# pushes first real line of output
# to the line after the terminal garbage finishes
# "garbage" is due to mismatch in terminal speed on boot, not a bug
print("booting")

# # convert hex into readable mac address
# RAW_MAC = espnowex.get_mac()
# MY_MAC = ':'.join(['{:02x}'.format(b) for b in RAW_MAC])
# # print(f"My MAC:: {MY_MAC}")
# print(f"My MAC addres:: {MY_MAC} raw MAC:: {RAW_MAC}")

# print("send a demo packet")
# espnowex.demo_send()
