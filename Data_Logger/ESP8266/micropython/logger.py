import os
import realtc
import time
import sd
import conf

# documentation of system call for total space from root '//'
# os.statvfs('//')
# f_bsize − preferred file system block size.
# f_frsize − fundamental file system block size.
# f_blocks − total number of blocks in the filesystem.
# f_bfree − total number of free blocks.
# f_bavail − free blocks available to non-super user.
# f_files − total number of file nodes.
# f_ffree − total number of free file nodes.
# f_favail − free nodes available to non-super user.
# f_flag − system dependent.
# f_namemax − maximum file name length.


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


def write_log(filename, data):
    """write out a CSV record starting with current system"""
    mnt = '/' + conf.LOG_MOUNT
    sd.initSD(mnt)
    with open(filename, "a") as f:
        f.write(f"{realtc.formattime(time.localtime())},{data}")
        f.write("\n")
    sd.closeSD(mnt)


def cat_log(filename):
    with open(filename, "r") as f:
        for line in f:
            print(line.rstrip())
    print("end of log")
