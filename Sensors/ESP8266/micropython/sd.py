# CUSTOM CODE TO MOUNT MICROSD CARD
# DATA SHOULD GO TO /mnt/log/

import machine, sdcard, os
from machine import Pin, SPI
import time


def initSD(mnt):
    print(f"mounting {mnt}")
    sd = sdcard.SDCard(machine.SPI(1), machine.Pin(15))
    vfs = os.VfsFat(sd)
    os.mount(vfs, mnt)
    # os.listdir(mnt)
    # time.sleep(0.2)
    listFiles = os.listdir(mnt)
    if len(listFiles) > 0:
        print(f"file(s) in {mnt} {listFiles}")
    else:
        print("no file!")


def closeSD(mnt):
    os.umount(mnt)


# vfs = os.VfsFat(sd)
# os.mount(vfs, “/fc”)

# fn = "/fc/one-line-log.txt"
# print()
# print("Single block write")
# with open(fn, "a") as f:
#     n = f.write('1234567890\n')  # one block
#     print(n, "bytes written")


# code8-1 : list
# import sdcard, os
# from machine import Pin, SPI
# กำหนดขา CS
# sdCSPin = Pin(15)
# using SPI port 1
# spi = SPI(1)
# create object sdcard
# sd = sdcard.SDCard(spi, sdCSPin)
# # connected to folder /sd
# os.mount(sd, '/sd')
# # read files list in /sd
# listFiles = os.listdir('/sd')
# if len(listFiles) > 0:
#     print("{file(s) in /sd}".format(listFiles))
# else:
#     print("no file!")
# unmount the folder
# os.umount('/sd')
# stop using SPI port
# spi.deinit()


# import machine, sdcard, os

# # MicroSD card adaptor is interfaced via SPI 1
# sd = sdcard.SDCard(machine.SPI(1), machine.Pin(3))

# # mount /fc as the sd card
# vfs = os.VfsFat(sd)
# os.mount(vfs, “/fc”)
# print(“Filesystem check”)
# print(os.listdir(“/fc”))

# # writing a single block in a text file on a MicroSD card
# fn = “/logs/one-line-log.txt”
# print()
# print(“Single block write”)
# with open(fn, “at”) as f:
#             n = f.write('1234567890\n')  # one block
#             print(n, “bytes written”)


# # reading a text file from a MicroSD card
# fn = “/logs/one-line-log.txt”
# print()
# print(“Single block read”)
# with open(fn, “rt”) as f:
#             result = f.read()
#             print(len(result2), “bytes read”)
#             print()
#             print(result)


# #writing multiple blocks in a text file on a MicroSD card
# line = 'abcdefghijklmnopqrstuvwxyz\n'
# lines = line * 200  # 5400 chars
# fn = “/fc/multi-line-log.txt”
# print()
# print(“Multiple block write”)
# with open(fn, “w”) as f:
#             n = f.write(lines)
#             print(n, “bytes written”)

# # reading multi-block text file from a MicroSD card.

# fn = “/fc/multi-line-log.txt”
# print()
# print(“Multiple block read”)
# with open(fn, “r”) as f:
#             result = f.read()
#             print(len(result2), “bytes read”)
#             print()
#             print(result)
