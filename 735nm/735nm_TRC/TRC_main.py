import sys
import time
import math
import machine
import conf
import realtc
import thermocouple
import espnowex
import gc
import random

# =================== try this?


rtc = machine.RTC()
random.seed(123)

def task():
    # Your task goes here
    # Functionised because we need to call it twice
    print(f"task() run at: {realtc.formattime(time.localtime())}")
    time.sleep(random.getrandbits(4)) # arbitrary time to complete testing
    gc.collect()
   # temperature_store()

def log_data(esp_con, tsec, interval, boundary):
    print(f"LOG THE DATA: {realtc.formattime(time.localtime())} ----------")
    out = "SYSLOG:" + ",".join([realtc.formattime(time.localtime()), "LOGGING TEST", str(tsec), str(interval), str(boundary)])
    [espnowex.esp_tx(logger, esp_con, out) for logger in conf.peers['DATA_LOGGER']]
    gc.collect()

def run(esp_con):
    interval = 15 * 60 # 15 minutes at (00, 15, 30, 45), value has to be in seconds, 
    # t = list()
    # [t.append(value) for value in range(0,60,2)]
    # print(f"interval:{interval}, t:{t}")
    # # last_min = 0

    # print(rtc.datetime())
    # # initialize to next valid minute boundary
    # print("\nSynchronize timing with the internal clock. This may take a while...")
    # print(f"The current starting minute is: {rtc.datetime()[5]}.")
    # print(f"Boundary minutes must start on a value of:{t}")
    # while rtc.datetime()[5] not in t: 
    #     time.sleep(1)
    # last_min = rtc.datetime()[5]
    # print(f"Synchronized on minute: {rtc.datetime()[5]} and set start of {last_min}")
    # print(f"It will reset when the minute is:{(last_min + interval)}\n")


    while True:
        # run one task before checking the interval in the loop
        # print("run initial task")    
        task()
        # print("intial task done\n")

        # we started on the correct boundary, not run on every interval
        # is as accurate as the clock, or how long the task takes to complete
        # have to shift to 0 to 59, 60 not valid
        # while rtc.datetime()[5] < (last_min + interval) % 60:
        ### need to add in second condition on if the elapsed seconds > interval * 60
        tsec = ((rtc.datetime()[5] * 60) + rtc.datetime()[6])
        boundary =  tsec % interval
        last_boundary = boundary

        while  (boundary != 0) and (last_boundary <= boundary):
            print(f"{realtc.formattime(time.localtime())}  tsec:{tsec}  boundary %:{boundary}  last boundary: {last_boundary}  interval:{interval}")
            # print(f"boundary != 0 {boundary != 0} - or - last_boundary <= boundary {last_boundary <= boundary} - total eval: {boundary != 0 or last_boundary <= boundary}")
            task() # run the collect data/average
            # print("task done, loop")

            tsec = ((rtc.datetime()[5] * 60) + rtc.datetime()[6])
            boundary =  tsec % interval
            if boundary > last_boundary:
                last_boundary = boundary

        # we took as long or longer than interval, increment interval
        # to get back to next boundary
        ### last_min = last_min + interval
        # out of look on boundary condition
        # send data to data logger
        log_data(esp_con, tsec, interval, boundary)
        print(f"Data Logged {realtc.formattime(time.localtime())} ----------")
        last_boundary = boundary

        print("=============== END ===================\n\n")

# ================================

def trc_main(esp_con, sta, RAW_MAC):
    print("START TEMPERATURE RELAY CONTROL SENSOR")
    run(esp_con)

    # relay control, start in the off state
    D8 = machine.Pin(15, machine.Pin.OUT)
    D8.off()

    sequence = 1  # record number from the last time the system restarted

    while True:
        readings = thermocouple.initReadings(conf.readings)
        readings, myReadings = thermocouple.read_thermocouples(readings)

        temperature_data, internal_data = thermocouple.allReadings(readings)
        org_data, org_inter = thermocouple.allReadings(myReadings)
        date_time, _, _ = realtc.formattime(time.localtime())
        gc.collect()
        MY_MAC = ":".join(["{:02x}".format(b) for b in RAW_MAC])

        out = ','.join([str(sequence), date_time, MY_MAC, temperature_data, internal_data])
        # print(f"Data Packet: {out}")
        # transmit to all conf DATA_LOGGER values
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

        time.sleep(5)
