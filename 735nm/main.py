import sys
import time
from math import isnan
import machine

# import program configuration
import conf
import realtc
import thermocouple
import espnowex
import calibrate
# import datalogger_main
# import BME280_main
# import TRC_main  


print("START SENSOR")


def get_remote_time():
    # con = espnowex.init_esp_connection()
    sta, ap = espnowex.wifi_reset()
    esp_con = espnowex.init_esp_connection(sta)

    # convert hex into readable mac address
    RAW_MAC = espnowex.get_mac(sta)
    MY_MAC = ":".join(["{:02x}".format(b) for b in RAW_MAC])
    # print(f"My MAC:: {MY_MAC}")
    print(f"My MAC addres:: {MY_MAC} raw MAC:: {RAW_MAC}")

    # set the time from the logger
    retries = 0
    host = ""
    
    # TODO this is old way, need to use conf.py values
    peer = b'\x8c\xaa\xb5M\x7f\x18'
    espnowex.esp_tx(peer, esp_con, "get_time")
    host, msg = espnowex.esp_rx(esp_con)

    while not msg:
        retries += 1
        espnowex.esp_tx(peer, esp_con, "get_time")
        # print("Time Sensor: wait for time response")
        host, msg = espnowex.esp_rx(esp_con)
        print(f"found host: {host}")
        print(f"Get Time: unable to get time ({retries})")
        time.sleep(3)

    print(host)
    str_host = ":".join(["{:02x}".format(b) for b in host])
    # assumption data is utf-8, if not, it may fail
    str_msg = msg.decode("utf-8")

    print("------------------------")
    print(f"received a respons from {host} {str_host} of: {msg}")
    et = eval(msg)
    print("--------------------")
    print(f"et: {et}")
    print("--------------------")

    rtc = machine.RTC()
    rtc.datetime(et)
    print(f"The new time is: {realtc.formattime(time.localtime())}")


def main():
    get_remote_time()
    print(f"time set and my role is {conf.MYROLE}")
    # use the conf.py file to select the roll of the device
    # and then call the appropriate startup
    if conf.MYROLE == "CALIBRATE":
        calibrate.calibrate_main()
    elif conf.MYROLE == "DATALOGGER":
        # call the data logger main here
        print("datalogger")
        # datalogger_main.data_looger_main()
    elif conf.MYROLE == "TRCCONTROL":
        print("tcr")
        TRC_main.main()
        # call the thermocouple and relay control main here
    elif conf.MYROLE == "THP":
        # call the temp/humidity/pressure main here
        print("THP")
        BME280_main.main()

        
    # D8 = machine.Pin(15, machine.Pin.OUT)
    # D8.off()

    # sequence = 1 # record number from the last time the system restarted

    # readings = thermocouple.initReadings(conf.readings)
    # readings, myReadings = thermocouple.read_thermocouples(readings)

    # # temperature_data = ', '.join([str(value[2]) for value in readings.values()])
    # temperature_data, internal_data = thermocouple.allReadings(readings)
    # org_data, org_inter = thermocouple.allReadings(myReadings)
    # date_time, _, _ = realtc.formattime(time.localtime())
    # out = ','.join([str(sequence), date_time, temperature_data, internal_data])
    print("--------THE SCRIPT ENDED--------")


if __name__ == "__main__":
    try:
        print(f"reset code: {machine.reset_cause()}")
        main()
    except KeyboardInterrupt as e:
        print(f"Got ctrl-c {e}")
        # D8.off() # TODO D8 HAS TO BE SET TO OFF ON ERROR !!!!!!!!!!!!!!!!!!
        sys.exit()  # TODO this falls through and resets???? okay for now
    finally:
        print(f"Fatal error, restarting.  {machine.reset_cause()}")
        # D8.off() # TODO D8 HAS TO BE SET TO OFF ON ERROR !!!!!!!!!!!!!!!!!!
        machine.reset()
