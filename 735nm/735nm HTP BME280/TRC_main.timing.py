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
    print(f"task() run at: {realtc.formattime(time.localtime())}")
    time.sleep(random.getrandbits(4)) # arbitrary time to complete testing
    gc.collect()

def log_data(esp_con, tsec, interval, boundary):
    print("\n\n=============== LOG_DATA ===================")
    print(f"---------- {realtc.formattime(time.localtime())} ----------\n")
    out = "SYSLOG:" + ",".join([realtc.formattime(time.localtime()), realtc.formattime(time.localtime())[:-3], "LOGGING TEST", str(tsec), str(interval), str(boundary)])
    [espnowex.esp_tx(logger, esp_con, out) for logger in conf.peers['DATA_LOGGER']]
    print(f"\n---------- {realtc.formattime(time.localtime())} ----------")
    print("=============== END =========================\n\n")
    gc.collect()

def run(esp_con):
    interval = 5 * 60 # 15 minutes at (00, 15, 30, 45), value has to be in seconds, 

    while True:
        # run one task before checking the interval in the loop
        task()

        # this is as accurate as the clock, or how long the task takes to complete
        # it will run on every 'interval' on the same time as clock
        # eg; 15 min interval (in seconds) will run every 15 minutes at (00, 15, 30, 45) minutes every hour
        # when the task copmletes, if the 'interval' is exceded, it runs that alternate log portion 
        curr_time = rtc.datetime()
        tsec = ((curr_time[5] * 60) + curr_time[6])
        boundary =  tsec % interval
        last_boundary = boundary

        # if the boundary happens to hit 0, or we have not gone over the interval run the task
        # while  (boundary != 0) and (last_boundary <= boundary):
        print(f"     BEFORE WHILE: {realtc.formattime(time.localtime())}  tsec:{tsec}  boundary %:{boundary}  last boundary: {last_boundary}  interval:{interval}")
        while (last_boundary == boundary): # case == 0 very rare, look at exceeding only
            print(f"LOOP ----- {realtc.formattime(time.localtime())}  tsec:{tsec}  boundary %:{boundary}  last boundary: {last_boundary}  interval:{interval}")
            # print(f"boundary != 0 {boundary != 0} - or - last_boundary <= boundary {last_boundary <= boundary} - total eval: {boundary != 0 or last_boundary <= boundary}")
            task() # run the task until interval is hit

            curr_time = rtc.datetime()
            tsec = ((curr_time[5] * 60) + curr_time[6])
            boundary = tsec % interval
            if boundary > last_boundary:
                last_boundary = boundary


        # interval was exceeded, run alternate code
        # send data to data logger
        print(f"NEED TO LOG DATA: {realtc.formattime(time.localtime())}  tsec:{tsec}  boundary %:{boundary}  last boundary: {last_boundary}  interval:{interval}")
        log_data(esp_con, tsec, interval, boundary)

        # reset interval checking
        realtc.get_remote_time(esp_con)
        curr_time = rtc.datetime()
        tsec = ((curr_time[5] * 60) + curr_time[6])
        boundary = tsec % interval
        last_boundary = boundary
        print(f"     RESET THE TIME: {realtc.formattime(time.localtime())}  tsec:{tsec}  boundary %:{boundary}  last boundary: {last_boundary}  interval:{interval}")


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
