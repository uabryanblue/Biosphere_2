import os
import machine
import realtc
import time
import conf
import uerrno  # error trapping and code values
import sdcard
import gc 
# import esp


def initSD(mnt):
    gc.collect()
    # print(f"mounting {mnt}")
    sd = sdcard.SDCard(machine.SPI(1), machine.Pin(15))
    # vfs = os.VfsFat(sd)
    # print(gc.mem_free())
    # print(esp.freemem())
    os.mount(sd, mnt)


def closeSD(mnt):
    gc.collect()
    try:
        # print(f"unmounting {mnt}")
        os.umount(mnt)
    except OSError as e:
        if e.args[0] == uerrno.ETIMEDOUT:  # standard timeout is okay, ignore it
            print("ETIMEDOUT found")  # timeout is okay, ignore it
        else:  # general case, continue processing, prevent hanging
            print(f"OSError: Connection closed {e}")



def get_free_space(mnt):
    """calculate total ree space, use '//' for total"""

    disk = os.statvfs(mnt)
    size_free = disk[0] * disk[4]
    return size_free


def get_storage_stats(mnt):
    """easy way to print common storage stats"""

    print(f"total space: {get_total_space(mnt)}")
    print(f"free space: {get_free_space(mnt)}")


def get_total_space(mnt):
    """calculate total storage available, use '//' for total"""

    disk = os.statvfs(mnt)
    total_storage = disk[0] * disk[2]
    return total_storage


def write_log(logname, data):
    """write out a CSV record starting with current system"""
    print(f"-----------storing to mount with filename:{logname}")
    outfile = conf.LOG_MOUNT + '/' + logname
    print(f"-----------storing: {outfile} mount:{conf.LOG_MOUNT} with filename:{logname}")

    initSD(conf.LOG_MOUNT)
    print("card initialized")
    with open(outfile, "a") as f:
        f.write(f"{realtc.formattime(time.localtime())}, {data}")
        f.write("\n")
    closeSD(conf.LOG_MOUNT)


def cat_log(filename):
    with open(filename, "r") as f:
        for line in f:
            print(line.rstrip())
    print("end of log")
