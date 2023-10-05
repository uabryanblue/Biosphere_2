import sys
import time
from math import isnan
import machine
import conf
import realtc
import thermocouple
import espnowex


def trc_main(esp_con, sta):
    print("START TEMPERATURE SENSOR")

    # relay control, start in the off state
    D8 = machine.Pin(15, machine.Pin.OUT)
    D8.off()

    sequence = 1 # record number from the last time the system restarted

    # convert hex into readable mac address
    # RAW_MAC, MY_MAC = espnowex.get_mac(sta)
    # output values for easier identification of the device
    # print(f"TRC RAW MAC addres: {RAW_MAC}")

    while True:
        readings = thermocouple.initReadings(conf.readings)
        readings, myReadings = thermocouple.read_thermocouples(readings)

        temperature_data, internal_data = thermocouple.allReadings(readings)
        org_data, org_inter = thermocouple.allReadings(myReadings)
        date_time, _, _ = realtc.formattime(time.localtime())
        out = ','.join([str(sequence), date_time, MY_MAC, temperature_data, internal_data])
        print(out)
        # transmit to all conf DATA_LOGGER values
        [espnowex.esp_tx(val, esp_con, out) for val in conf.peers['DATA_LOGGER']]

        # espnowex.esp_tx(conf.peers["DATA_LOGGER"][0], esp_con, out)
        sequence += 1
        # difference between treatment and control leaf handling
        # also check for heater going out of randge
        # and if temperature above maximum value for heating due to other reasons.
        diff = readings['TREATMENT'][2] - readings['CONTROL'][2]
        # print(f"CHECK TEMP DIFFERENCE - cont:{readings['CONTROL'][2]}, heat:{readings['TREATMENT'][2]}, DIFFERENCE: {diff}")
        
        if isnan(diff) is True:
            D8.off() # trouble reading sensor, turn off for safety TODO generate error in system log
        elif readings['HEATER'][2] >= conf.TMAX_HEATER: # error state, shut down heater
            D8.off() # TODO record an ERROR in the system log
        elif readings['TREATMENT'][2] >= conf.TMAX: # warning leaf temp exceeded threshold, turn off heater
            D8.off() # TODO record a WARNING in the system log
        # TODO there needs to be a deadband to prevent oscillation
        elif diff < (conf.TDIFF + 0.25): # lower than required temp above control leaf
            D8.on() 
        elif diff >= (conf.TDIFF - 0.25): # higher than required temp control leaf
            D8.off()

        time.sleep(5)







