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

    # setup 3 versions of mac for display, logging, tx/rx
    esp_con, station, RAW_MAC = init_device()
    gc.collect()
    MY_MAC = ":".join(["{:02x}".format(b) for b in RAW_MAC]).upper()
    MY_ID = "-".join(["{:02x}".format(b) for b in RAW_MAC]).upper()
    print(f"My MAC addres: {MY_MAC}\n ID: {MY_ID}\n raw: {RAW_MAC}")

    logger.write_log(conf.SYSTEM_LOG, f"{MY_MAC} data logger started")
    gc.collect()

    while True:
        print("Data Logger: listen for a message")
        D0.on()  # LED off as a visual aid
        host, msg = espnowex.esp_rx(esp_con, 10000)
        gc.collect()
        if host is not None:
            str_host = ":".join(["{:02x}".format(b) for b in host]).upper()
            log_host = "-".join(["{:02x}".format(b) for b in host]).upper()
            D0.off() # turn on indicate a message was received
            if host in conf.peers["REMOTE"]:
                print(f"VERIFIED ------- {host} is in my REMOTE list {conf.peers["REMOTE"]}")
                # str_host = ":".join(["{:02x}".format(b) for b in host])
        else:
            msg = b"NOT MY MAC"
            print(f"INVALID host ------- {host} not in my REMOTE list {conf.peers["REMOTE"]}")

        # assumption data is utf-8, if not, it may fail
        if msg is not None:
            str_msg = msg.decode("utf-8")
        else:
            str_msg = ''

        if msg == b"NOT MY MAC":
            print(f"MAC {host} not for me, ignoring.")

        # host is already verified to be one that should be processed
        elif msg == b"get_time":
            D0.off()  # turn on indicate a message was received
            # print(f"Data Logger: {host}, {str_host} requested the time")

            # tx_mac = ":".join(["{:02x}".format(b) for b in host]).upper()
            sys_msg = f"Time requested by: {str_host}"
            logger.write_log(conf.SYSTEM_LOG, sys_msg)
                        
            # receiver blocked until time is received
            espnowex.esp_tx(host, esp_con, str(rtc.datetime()))
            gc.collect()

            sys_msg = f"Time sent to: {str_host}"
            print(sys_msg)
            logger.write_log(conf.SYSTEM_LOG, sys_msg)

            D0.on()  # turn led off, finished rquest
        elif "CALIBRATE:" in str_msg:
            # log_mac = "_".join(["{:02x}".format(b) for b in host]).upper()
            log_name = f"calibrate_{log_host}.log"
            print(f"CALIBRATE: storing to {log_name} - {str_msg[10:]}")
            # remove the word CALIBRATE: and store the rest
            logger.write_log(log_name, str_msg[10:])
            gc.collect()
        else:
            try:
                D0.off()  # turn on indicate a message was received
                # it is assumed the date/time and record number are part of str_msg
                log_name = f"{log_host}.log"
                # each device has it's own log
                # LOGNAME = conf.LOG_MOUNT + '/' + MsgHost
                print(f"MAC {host} is for me, storing to {log_name}")
                logger.write_log(log_name, str_msg)
                # logger.write_log(LOGNAME, str_host + "," + str_msg)
                D0.on()  # turn off led
            except OSError as e:
                D0.off()  # turn LED off as a visual aid for error
                if e.args[0] == uerrno.ETIMEDOUT:  # standard timeout is okay, ignore it
                    print("ETIMEDOUT found")  # timeout is okay, ignore it
                else:  # general case, continue processing, prevent hanging
                    # TODO -------------- WRITE LOG ERROR: [Errno 1] EPERM needs trapped, a reset is in order
                    print(f"-------------- WRITE LOG ERROR: {e}")


if __name__ == "__main__":
    try:
        print(f"rest code: {machine.reset_cause()}")
        main()
    except KeyboardInterrupt as e:
        print(f"Got ctrl-c {e}")
        logger.closeSD()
        logger.closeSD(conf.LOG_MOUNT)
    finally:
        print(f"Fatal error, restarting.  {machine.reset_cause()}")
        logger.closeSD(conf.LOG_MOUNT)
        machine.reset()
