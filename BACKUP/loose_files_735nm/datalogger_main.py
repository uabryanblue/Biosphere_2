# import sys
import time
import machine
# import uerrno

import logger
import conf
import realtc
import sd

import espnowex


def data_looger_main(esp_con, station, RAW_MAC):
    # # set the on board RTC to the time from the DS3231
    realtc.rtcinit()
    # print("set time")

    print("START DATA LOGGER")

    # status pin for logger, GPIO16/D0
    D0 = machine.Pin(16, machine.Pin.OUT)
    D0.off()  # turn led on

    # rtc = machine.RTC()

    # # convert hex into readable mac address
    # # RAW_MAC, MY_MAC = espnowex.get_mac(station)
    # MY_MAC = ":".join(["{:02x}".format(b) for b in RAW_MAC])
    # # print(f"My MAC addres:: {MY_MAC} raw MAC:: {RAW_MAC}")
    # print("going to write")
    # logger.write_log(conf.SYSTEM_LOG, f"{MY_MAC} data logger started")
    # print("wrote, enter loop")
    while True:
        print("Data Logger: listen for a message")
        D0.on()  # turn led off as a visual aid
        host, msg = espnowex.esp_rx(esp_con, 10000)
        if host is not None:
            str_host = ":".join(["{:02x}".format(b) for b in host])
            # D0.off() # turn on indicate a message was received
        else:
            msg = b"ERROR"
            # TODO error should be generic

        # assumption data is utf-8, if not, it may fail
        str_msg = msg.decode("utf-8")

        if msg == b"get_time":
            D0.off()  # turn on indicate a message was received
            print(f"Data Logger: {host}, {str_host} requested the time")

            # TODO turn into function
            tx_mac = ":".join(["{:02x}".format(b) for b in host]).upper()
            sys_msg = f"Time requested by: {tx_mac}"
            logger.write_log(conf.SYSTEM_LOG, sys_msg)

            time.sleep(0.1)  # let other side get ready
            # receiver blocked until time is received
            espnowex.esp_tx(host, esp_con, str(rtc.datetime()))

            # human readable with ":" seperators
            tx_mac = ":".join(["{:02x}".format(b) for b in host]).upper()
            sys_msg = f"Time sent to: {tx_mac}"
            print(sys_msg)
            logger.write_log(conf.SYSTEM_LOG, sys_msg)

            D0.on()  # turn led off, finished rquest
        elif msg == b"ERROR":
            print("No Messages")  # normally this is a timeout, just continue
        else:
            try:
                D0.off()  # turn on indicate a message was received
                # transform raw mac into a name that is suitable as a filename
                # each device has it's own log
                MsgHost = "-".join(["{:02x}".format(b) for b in host]).upper() + ".log"
                logger.write_log(MsgHost, str_msg)
                D0.on()  # turn off led
            except OSError as e:
                D0.off()  # turn LED on as a visual aid for error
                # if e.args[0] == uerrno.ETIMEDOUT:  # standard timeout is okay, ignore it
                #     print("ETIMEDOUT found")  # timeout is okay, ignore it
                # else:  # general case, continue processing, prevent hanging
                #     # TODO -------------- WRITE LOG ERROR: [Errno 1] EPERM needs trapped, a reset is in order
                #     print(f"-------------- WRITE LOG ERROR: {e}")

    # ########### !!! for safety if you don't close the mnt it will get overwritten
    # when the next PYMAKR update is performed!!!!!!!!!!!
    # sd.closeSD(conf.LOG_MOUNT)
