# import os
import realtc
import time
import sd
import conf

# use "//" to get size from root, on chip memory
# use "//mnt" for any mount named "mnt" stats
# Example: os.statvfs('//')
# f_bsize = 0 # preferred file system block size.
# f_frsize = 1 # fundamental file system block size.
# f_blocks = 2 # total number of blocks in the filesystem.
# f_bfree = 3 # total number of free blocks.
# f_bavail = 4 # free blocks available to non-super user.
# f_files = 5 # total number of file nodes.
# f_ffree = 6 # total number of free file nodes.
# f_favail = 7 # free nodes available to non-super user.
# f_flag = 8 # system dependent.
# f_namemax = 9 # maximum file name length.


# def get_storage_free_space(mnt):
#     """calculate total ree space, use '//' for total"""

#     storage = os.statvfs(mnt)
#     # block size * blocks available
#     free = storage[f_bsize] * storage[f_bavail]
#     return free

# def get_storage_total(mnt):
#     """calculate total storage available, use '//' for total"""

#     storage = os.statvfs(mnt)
#     # block size * total blocks available
#     total_storage = storage[f_bsize] * storage[f_blocks]
#     return total_storage


def write_log(filename, data):
    """write out a CSV record starting with current system"""
    # print(f"-----------storing to mount with filename:{filename}")
    sd.initSD(conf.LOG_MOUNT)
    with open(filename, "a") as f:
        f.write(f"{realtc.formattime(time.localtime())}, {data}")
        f.write("\n")
    sd.closeSD(conf.LOG_MOUNT)


# def cat_log(filename):
#     """dump contents of filename to the terminal"""
#     sd.initSD(conf.LOG_MOUNT)
#     with open(filename, "r") as f:
#         for line in f:
#             print(line.rstrip())
#     print("end of log")
#     sd.closeSD(conf.LOG_MOUNT)
