import time
import machine
import uerrno

import logger
import conf
import realtc
import espnowex
import gc

def data_looger_main(esp_con, station, RAW_MAC):
    # set the on board RTC to the time from the DS3231
    print(f"main start {gc.mem_free()}")
    realtc.rtcinit()
    # print("set time")

    print("START DATA LOGGER")
    # status pin for logger, GPIO16/D0
    D0 = machine.Pin(16, machine.Pin.OUT)
    D0.off()  # turn led on

    rtc = machine.RTC()
    RAW_MAC = bytearray()
    RAW_MAC = espnowex.get_mac(station)

    while True:
        print("Data Logger: listen for a message")
        D0.on()  # turn led off as a visual aid
        host, msg = espnowex.esp_rx(esp_con, 10000)
        # get a message, but it must be sent to my mac address

        # if host is not None and host == RAW_MAC:
        if host in conf.peers["REMOTE"]:
            print(f"VERIFIED ------- {host} is in my REMOTE list {conf.peers["REMOTE"]}")
            str_host = ":".join(["{:02x}".format(b) for b in host])
        else:
            msg = b"NOT MY MAC"
            print(f"INVALID host ------- {host} not in my REMOTE list {conf.peers["REMOTE"]}")
        print(f"before {gc.mem_free()}")
        gc.collect()
        print(f"after {gc.mem_free()}")
        # if host == RAW_MAC:
        #     str_host = ":".join(["{:02x}".format(b) for b in host])
        #     print(f"my str host: {str_host}")
        #     # D0.off() # turn on indicate a message was received
        # ovveride the message when conditions are not met
    #     elif host != RAW_MAC:
    #         msg = b"NOT MY MAC"
    #         print(f"Message not for me: {host} != {RAW_MAC}")
    # #     else:
    #         # change msg to error for further processing
    #         msg = b"ERROR"
    #         # TODO error should be generic

        # assumption data is utf-8, if not, it may fail
        str_msg = msg.decode("utf-8")
        if msg == b"get_time":
            D0.off()  # turn on indicate a message was received
            # print(f"Data Logger: {host}, {str_host} requested the time")

            # TODO turn into function
            tx_mac = ":".join(["{:02x}".format(b) for b in host]).upper()
            sys_msg = f"Time requested by: {tx_mac}\n"

            print(f"-write to log: {sys_msg}-")
            print(f"wl before {gc.mem_free()}")
            gc.collect()
            print(f"wl after {gc.mem_free()}")
            logger.write_log(conf.SYSTEM_LOG, sys_msg)
            # print("WROTE TO LOG!\n")

            # time.sleep(0.1)  # let other side get ready
            # receiver blocked until time is received
            # espnowex.esp_tx(host, esp_con, str(rtc.datetime()))

            # human readable with ":" seperators
            # tx_mac = ":".join(["{:02x}".format(b) for b in host]).upper()
            # sys_msg = f"Time sent to: {tx_mac}"
            # print(sys_msg)
    #         logger.write_log(conf.SYSTEM_LOG, sys_msg)

    #         D0.on()  # turn led off, finished rquest
        else:
            try:
                D0.off()  # turn on indicate a message was received
                # transform raw mac into a name that is suitable as a filename
                # each device has it's own log
                MsgHost = "-".join(["{:02x}".format(b) for b in host]).upper() + ".log"
                # logger.write_log(MsgHost, str_msg)
                D0.on()  # turn off led
            except OSError as e:
                D0.off()  # turn LED on as a visual aid for error
                if e.args[0] == uerrno.ETIMEDOUT:  # standard timeout is okay, ignore it
                    print("ETIMEDOUT found")  # timeout is okay, ignore it
                else:  # general case, continue processing, prevent hanging
                    # TODO -------------- WRITE LOG ERROR: [Errno 1] EPERM needs trapped, a reset is in order
                    print(f"-------------- WRITE LOG ERROR: {e}")

    # # ########### !!! for safety if you don't close the mnt it will get overwritten
    # # when the next PYMAKR update is performed!!!!!!!!!!!
    # # sd.closeSD(conf.LOG_MOUNT)
