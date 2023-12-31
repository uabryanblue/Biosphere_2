
import machine
import conf
import realtc
import espnowex
import time

# CHECK THE BLOCK OF ROLES
# import calibrate
# import datalogger_main
# import BME280_main
import TRC_main

# visual 5 second led on startup
# status pin for logger, GPIO16/D0
D0 = machine.Pin(16, machine.Pin.OUT)
D0.off() # visual we started
# slow any restart loops
time.sleep(5)
D0.on() # turn off
del D0 

D8 = machine.Pin(15, machine.Pin.OUT)
def init_device():

    # turn off wifi and connect with ESPNow
    sta, ap = espnowex.wifi_reset()
    esp_con = espnowex.init_esp_connection(sta)

    # convert hex into readable mac address
    RAW_MAC = espnowex.get_mac(sta)
    MY_MAC = ":".join(["{:02x}".format(b) for b in RAW_MAC])
    print(f"My MAC addres:: {MY_MAC} raw MAC:: {RAW_MAC}")

    return esp_con, sta, RAW_MAC


def main():
    print("--------START DEVICE--------")
    esp_con, station, RAW_MAC = init_device()
    # relay control, start in the off state
    D8.off()

    # verify that the conf.py file is associated with this code base
    if conf.MYROLE == "TRCCONTROL":
        print("\n================ MY CONFIGURATION ================")
        print("MY DATA LOGGERS")
        [print(val) for val in conf.peers['DATA_LOGGER']]
        print("MY TIME SERVER")
        [print(val) for val in conf.peers['TIME']]
        print("================ MY CONFIGURATION ================\n")


        realtc.get_remote_time(esp_con)
        TRC_main.trc_main(esp_con, station, RAW_MAC)
    else:
        print(f'MY ROLE IS {CONF.MYROLE} BUT IT SHOULD BE "TRCCONTROL".')
        print('!!!!!!!!invalid conf.py file!!!!!!!!')
        # TODO send an error message recorded in the datalogger syslog


if __name__ == "__main__":
    try:
        print(f"reset code: {machine.reset_cause()}")
        D8.off() # TODO D8 HAS TO BE SET TO OFF ON ERROR !!!!!!!!!!!!!!!!!!
        main()
    except KeyboardInterrupt as e:
        print(f"Got ctrl-c {e}")
        D8.off() # TODO D8 HAS TO BE SET TO OFF ON ERROR !!!!!!!!!!!!!!!!!!
        # sys.exit()  # TODO this falls through and resets???? okay for now
    finally:
        print(f"Fatal error, restarting.  {machine.reset_cause()}")
        D8.off() # TODO D8 HAS TO BE SET TO OFF ON ERROR !!!!!!!!!!!!!!!!!!
        machine.reset()
