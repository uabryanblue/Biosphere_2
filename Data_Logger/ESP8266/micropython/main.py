import sys
import time
import machine
import uerrno

import logger
import conf
import realtc
import sd

import espnowex

def main():
    # set the on board RTC to the time from the DS3231
    realtc.rtcinit()
    print("set time")

    print("START DATA LOGGER")
    # status pin for logger, GPIO16/D0
    D0 = machine.Pin(16, machine.Pin.OUT)
    D0.on()

    rtc = machine.RTC()

    sta, ap = espnowex.wifi_reset()
    esp_con = espnowex.init_esp_connection(sta)

    # convert hex into readable mac address
    RAW_MAC = espnowex.get_mac(sta)
    MY_MAC = ":".join(["{:02x}".format(b) for b in RAW_MAC]).upper()
    MY_ID = "-".join(["{:02x}".format(b) for b in RAW_MAC]).upper()
    print(f"My MAC addres: {MY_MAC} raw: {RAW_MAC}")

    # LOGNAME = conf.LOG_MOUNT + '/' + conf.LOG_FILENAME
    SYSLOG =  conf.LOG_MOUNT + '/' + conf.SYSTEM_LOG

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
            logger.write_log(SYSLOG, sys_msg)

            time.sleep(0.1)  # let other side get ready
            # receiver blocked until time is received
            espnowex.esp_tx(host, esp_con, str(rtc.datetime()))

            # TODO turn into function (see above)
            tx_mac = ":".join(["{:02x}".format(b) for b in host]).upper()
            sys_msg = f"Time sent to: {tx_mac}"
            print(sys_msg)
            logger.write_log(SYSLOG, sys_msg)

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
                logger.write_log(LOGNAME, str_host + "," + str_msg)
                D0.on()  # turn off led
            except OSError as e:
                D0.off()  # turn LED off as a visual aid for error
                if e.args[0] == uerrno.ETIMEDOUT:  # standard timeout is okay, ignore it
                    print("ETIMEDOUT found")  # timeout is okay, ignore it
                else:  # general case, continue processing, prevent hanging
                    print(f"-------------- WRITE LOG ERROR: {e}")
                    time.sleep(5)

    # ########### !!! if you don't close it, it will get overwritten
    # when the next PYMAKR update is performed!!!!!!!!!!!
    sd.closeSD(conf.LOG_MOUNT)


if __name__ == "__main__":
    try:
        print(f"rest code: {machine.reset_cause()}")
        main()
    except KeyboardInterrupt as e:
        print(f"Got ctrl-c {e}")
        sd.closeSD(conf.LOG_MOUNT)
        sys.exit()  # TODO this falls through and resets???? okay for now
    finally:
        print(f"Fatal error, restarting.  {machine.reset_cause()}")
        sd.closeSD(conf.LOG_MOUNT)
        machine.reset()
