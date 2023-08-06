import os
import machine
import realtc
import time
import sdcard
import conf

def initSD(mnt):
    # print(f"mounting {mnt}")
    sd = sdcard.SDCard(machine.SPI(1), machine.Pin(15))
    os.mount(sd, mnt)

def closeSD(mnt):
    try:
        # print(f"unmounting {mnt}")
        os.umount(mnt)
    except OSError as e:
        if e.args[0] == uerrno.ETIMEDOUT:  # standard timeout is okay, ignore it
            print("ETIMEDOUT found")  # timeout is okay, ignore it
        else:  # general case, continue processing, prevent hanging
            print(f"OSError: Connection closed {e}")

def write_log(filename, data):
    """write out a CSV record starting with current system"""
    # print(f"starting write_log for {filename} with {data}")
    outfile = conf.LOG_MOUNT + '/' + filename
    print(f"-----------storing: {outfile} mount:{conf.LOG_MOUNT} with filename:{filename}")
    initSD(conf.LOG_MOUNT)
    print("inited")
    with open(outfile, "a") as f:
        f.write(f"{realtc.formattime(time.localtime())}, {data}")
        f.write("\n")
    closeSD(conf.LOG_MOUNT)


# def cat_log(filename):
#     """dump contents of filename to the terminal"""
#     sd.initSD(conf.LOG_MOUNT)
#     with open(filename, "r") as f:
#         for line in f:
#             print(line.rstrip())
#     print("end of log")
#     sd.closeSD(conf.LOG_MOUNT)
