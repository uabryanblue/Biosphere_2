import time
import machine
import uerrno
import gc
import logger
import conf
import realtc

import espnowex

# status pin for logger, GPIO16/D0
D0 = machine.Pin(16, machine.Pin.OUT)
D0.off() # visual we started
# slow any restart loops
time.sleep(5)


def init_device():
    # turn off wifi and connect with ESPNow
    sta, _ = espnowex.wifi_reset()
    esp_con = espnowex.init_esp_connection(sta)
    # set the on board RTC to the time from the DS3231
    realtc.rtcinit()
    gc.collect()

    # convert hex into readable mac address
    RAW_MAC = espnowex.get_mac(sta)
    # print(f"My MAC addres:: {MY_MAC} raw MAC:: {RAW_MAC}")

    return esp_con, sta, RAW_MAC

def main():

    print("START DATA LOGGER")
    rtc = machine.RTC()
    gc.collect()
    # turn off wifi and ESPNow on
    esp_con, station, RAW_MAC = init_device()
    D0.on() # visual the intialization is done
    gc.collect()

    # RAW_MAC is b"" object
    MY_MAC = ":".join(["{:02x}".format(b) for b in RAW_MAC]).upper() # human readable
    MY_ID = "".join(["{:02x}".format(b) for b in RAW_MAC]).upper() # no delimiters for filenames
    print(f"My MAC addres: {MY_MAC}\n ID: {MY_ID}\n raw: {RAW_MAC}")
    gc.collect()
    syslog = f"{MY_ID}_{conf.SYSTEM_LOG}"
    logger.write_log(syslog, f"{MY_MAC} data logger started")
    gc.collect()

    while True:
        print("Data Logger: listen for a message")
        D0.on()  # LED off as a visual aid
        host, msg = espnowex.esp_rx(esp_con, 10000)
        realtc.rtcinit()
        gc.collect()
        if host is not None:
            str_host = ":".join(["{:02x}".format(b) for b in host]).upper()
            log_host = "".join(["{:02x}".format(b) for b in host]).upper() # for log names
            D0.off() # turn on indicate a message was received
            if host in conf.peers["REMOTE"]:
                print(f"VERIFIED ------- {host} is in my remote list") #  {conf.peers["REMOTE"]}")
        else:
            msg = b"NOT MY MAC"
            # print(f"INVALID host ------- {host} not in my REMOTE list {conf.peers["REMOTE"]}")

        # assumption data is utf-8, if not, it may fail
        if msg is not None:
            str_msg = msg.decode("utf-8")
        else:
            str_msg = ''

        D0.off()  # turn on indicate a message was received
        if msg == b"NOT MY MAC":
            if host is not None:
                print(f"Ignoring MAC {host} traffic. REMOTE list {conf.peers["REMOTE"]}.")
        elif msg == b"GET_TIME":
            sys_msg = f"{str_host} requested time"
            log_name = f"{MY_ID}_{conf.SYSTEM_LOG}"
            logger.write_log(log_name, sys_msg)
                        
            # receiver blocked until time is received
            stime = str(rtc.datetime())
            espnowex.esp_tx(host, esp_con, stime)
            gc.collect()

            sys_msg = f"{log_name} time sent {stime}"
            print(sys_msg)
            logger.write_log(log_name, sys_msg)
            gc.collect()
        elif "CALIBRATE:" in str_msg:
            log_name = f"{MY_ID}_CALIBRATE_{log_host}.log"
            print(f"CALIBRATE: storing to {log_name} - {str_msg[10:]}")
            # remove the word CALIBRATE: and store the rest
            logger.write_log(log_name, str_msg[10:])
            D0.on()  # turn led off, finished rquest
            gc.collect()
        elif "CLIMATE:" in str_msg:
            log_name = f"{MY_ID}_CLIMATE_{log_host}.log"
            print(f"CLIMATE: storing to {log_name} - {str_msg[7:]}")
            # remove the word CALIBRATE: and store the rest
            logger.write_log(log_name, str_msg[7:])
            D0.on()  # turn led off, finished rquest
            gc.collect()
        elif "SYSLOG:" in str_msg:
            log_name = f"{MY_ID}_SYSLOG_{log_host}.log"
            print(f"SYSLOG: storing to {log_name} - {str_msg[7:]}")
            logger.write_log(log_name, str_msg[7:])
            D0.on()  # turn led off, finished rquest
            gc.collect()
        else:
            # it is assumed the date/time and source MAC are part of str_msg
            log_name = f"{MY_ID}_TRC_{log_host}.log"
            print(f"TRC: storing to {log_name} - {str_msg}")
            logger.write_log(log_name, str_msg)
            D0.on()  # turn off led
            gc.collect()
        D0.on()  # turn led off, finished rquest


if __name__ == "__main__":
    try:
        print(f"rest code: {machine.reset_cause()}")
        main()
    except KeyboardInterrupt as e:
        print(f"Got ctrl-c {e}")
        D0.on() # turn led off
        logger.closeSD(conf.LOG_MOUNT)
    finally:
        print(f"Fatal error, restarting.  {machine.reset_cause()} !!!!!!!!!!!")
        time.sleep(1)
        D0.off() # turn led on
        time.sleep(1)
        D0.on() # turn led off
        logger.closeSD(conf.LOG_MOUNT)
        machine.reset()
