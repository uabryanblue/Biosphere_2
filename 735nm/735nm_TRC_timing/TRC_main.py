import sys
import time
import math
import machine
import conf
import realtc
import thermocouple
import espnowex
import gc


def trc_main(esp_con, sta, RAW_MAC):
    print("START TEMPERATURE RELAY CONTROL SENSOR")

    # relay control, start in the off state
    D8 = machine.Pin(15, machine.Pin.OUT)
    D8.off()

    # record number from the last time the system restarted
    sequence = 1
    
    while True:
        readings = thermocouple.initReadings(conf.readings)
        readings, myReadings = thermocouple.read_thermocouples(readings)

        temperature_data, internal_data = thermocouple.allReadings(readings)
        org_data, org_inter = thermocouple.allReadings(myReadings)
        date_time = realtc.formattime(time.localtime())
        gc.collect()
        MY_MAC = ":".join(["{:02x}".format(b) for b in RAW_MAC])

        out = ','.join([str(sequence), date_time, MY_MAC, temperature_data, internal_data])
        # print(f"Data Packet: {out}")
        # transmit to all conf DATA_LOGGER values
        out = "TRC:" + out
        [espnowex.esp_tx(logger, esp_con, out) for logger in conf.peers['DATA_LOGGER']]
        sequence += 1
        gc.collect()
        # difference between treatment and control leaf handling
        # also check for heater going out of randge
        # and if temperature above maximum value for heating due to other reasons.
        diff = readings['TREATMENT'][2] - readings['CONTROL'][2]
        # print(f"CHECK TEMP DIFFERENCE - cont:{readings['CONTROL'][2]}, heat:{readings['TREATMENT'][2]}, DIFFERENCE: {diff}")

        if math.isnan(diff) is True:
            D8.off()  # trouble reading sensor, turn off for safety TODO generate error in system log
        elif readings['HEATER'][2] >= conf.TMAX_HEATER:  # error state, shut down heater
            D8.off()  # TODO record an ERROR in the system log
        elif readings['TREATMENT'][2] >= conf.TMAX:  # warning leaf temp exceeded threshold, turn off heater
            D8.off()  # TODO record a WARNING in the system log
        # TODO there needs to be a deadband to prevent oscillation
        elif diff < (conf.TDIFF + 0.25):  # lower than required temp above control leaf
            D8.on()
        elif diff >= (conf.TDIFF - 0.25):  # higher than required temp control leaf
            D8.off()

        time.sleep_ms(int(conf.SAMPLE_INTERVAL/3))
