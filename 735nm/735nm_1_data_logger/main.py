import sys
import time
import machine
import uerrno
import gc
import logger
import conf
import realtc

import espnowex


def init_device():
    # turn off wifi and connect with ESPNow
    sta, ap = espnowex.wifi_reset()
    esp_con = espnowex.init_esp_connection(sta)

    # set the on board RTC to the time from the DS3231
    realtc.rtcinit()
    print("set time")

    # convert hex into readable mac address
    RAW_MAC = espnowex.get_mac(sta)
    # print(f"My MAC addres:: {MY_MAC} raw MAC:: {RAW_MAC}")

    return esp_con, sta, RAW_MAC

def main():

    print("START DATA LOGGER")
    rtc = machine.RTC()
 
    # status pin for logger, GPIO16/D0
    D0 = machine.Pin(16, machine.Pin.OUT)
    D0.on()

    gc.collect()
    esp_con, station, RAW_MAC = init_device()


    # station, ap = espnowex.wifi_reset()
    # esp_con = espnowex.init_esp_connection(station)
    # RAW_MAC = bytearray()
    # RAW_MAC = espnowex.get_mac(station)
    
    # convert hex into readable mac address
    
    
    MY_MAC = ":".join(["{:02x}".format(b) for b in RAW_MAC]).upper()
    MY_ID = "-".join(["{:02x}".format(b) for b in RAW_MAC]).upper()
    print(f"My MAC addres: {MY_MAC} raw: {RAW_MAC}")

    logger.write_log(conf.SYSTEM_LOG, f"{MY_MAC} data logger started")

    while True:
        print("Data Logger: listen for a message")
        D0.on()  # reset LED off as a visual aid
        host, msg = espnowex.esp_rx(esp_con, 10000)
        if host is not None:
            str_host = ":".join(["{:02x}".format(b) for b in host])
            # D0.off() # turn on indicate a message was received
        else:
            msg = b"ERROR"  # TODO error should be generic

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

            # TODO turn into function (see above)
            tx_mac = ":".join(["{:02x}".format(b) for b in host]).upper()
            sys_msg = f"Time sent to: {tx_mac}"
            print(sys_msg)
            logger.write_log(conf.SYSTEM_LOG, sys_msg)

            D0.on()  # turn led off, finished rquest
        elif msg == b"ERROR":  # TODO generic trap
            print("No Messages")  # normally this is a timeout, just continue
        else:
            try:
                D0.off()  # turn on indicate a message was received
                # it is assumed the date/time and record number are part of str_msg
                MsgHost = "-".join(["{:02x}".format(b) for b in host]).upper() + ".log"
                # each device has it's own log
                LOGNAME = conf.LOG_MOUNT + '/' + MsgHost
                logger.write_log(conf.LOG_FILENAME, str_msg)
                # logger.write_log(LOGNAME, str_host + "," + str_msg)
                D0.on()  # turn off led
            except OSError as e:
                D0.off()  # turn LED off as a visual aid for error
                if e.args[0] == uerrno.ETIMEDOUT:  # standard timeout is okay, ignore it
                    print("ETIMEDOUT found")  # timeout is okay, ignore it
                else:  # general case, continue processing, prevent hanging
                    # TODO -------------- WRITE LOG ERROR: [Errno 1] EPERM needs trapped, a reset is in order
                    print(f"-------------- WRITE LOG ERROR: {e}")

    # ########### !!! if you don't close it, it will get overwritten
    # when the next PYMAKR update is performed!!!!!!!!!!!
    logger.closeSD(conf.LOG_MOUNT)


if __name__ == "__main__":
    try:
        print(f"rest code: {machine.reset_cause()}")
        main()
    except KeyboardInterrupt as e:
        print(f"Got ctrl-c {e}")
        logger.closeSD(conf.LOG_MOUNT)
        sys.exit()  # TODO this falls through and resets???? okay for now
    finally:
        print(f"Fatal error, restarting.  {machine.reset_cause()}")
        logger.closeSD(conf.LOG_MOUNT)
        machine.reset()
