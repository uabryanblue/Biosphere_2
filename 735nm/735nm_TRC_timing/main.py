
import gc
import machine
import conf
import realtc
import espnowex
gc.collect()
import time
import sys
import math
import thermocouple
gc.collect()
import TRC_main


rtc = machine.RTC()
# CHECK THE BLOCK OF ROLES
# import calibrate
# import datalogger_main
# import BME280_main



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
    gc.collect()
    MY_MAC = ":".join(["{:02x}".format(b) for b in RAW_MAC])
    print(f"My MAC addres:: {MY_MAC} raw MAC:: {RAW_MAC}")

    return esp_con, sta, RAW_MAC


def main():
    print("--------START DEVICE--------")
    esp_con, station, RAW_MAC = init_device()

    # relay control, start in the off state
    D8 = machine.Pin(15, machine.Pin.OUT)
    D8.off()
    gc.collect()

    # verify that the conf.py file is associated with this code base
    if conf.MYROLE == "TRC":
        print("\n================ MY CONFIGURATION ================")
        print("MY DATA LOGGERS")
        [print(val) for val in conf.peers['DATA_LOGGER']]
        print("MY TIME SERVER")
        [print(val) for val in conf.peers['TIME']]
        print("================ MY CONFIGURATION ================\n")

        realtc.get_remote_time(esp_con)
        gc.collect()
    else:
        print(f'MY ROLE IS {conf.MYROLE} BUT IT SHOULD BE "TRC".')
        print('!!!!!!!!invalid conf.py file!!!!!!!!')

# ########################################################
#        TRC_main.trc_main(esp_con, station, RAW_MAC)
# ########################################################
# PUT REPLACEMENT MAIN CODE HERE

    # convert hex into readable mac address
    MY_MAC = ":".join(["{:02x}".format(b) for b in RAW_MAC])
    MY_ID = "".join(["{:02x}".format(b) for b in RAW_MAC]).upper()
    print(f"My MAC addres:: {MY_MAC} RAW MAC:: {RAW_MAC}")
    
    # sync date/time before starting
    realtc.get_remote_time(esp_con)
    gc.collect()

    # ---------- INSERT MACHINE SETUP
    tspi = machine.SPI(1, baudrate=5000000, polarity=0, phase=0)

    # initialize variables
    interval = conf.SAMPLE_INTERVAL # number ms to average readings
    log_interval = conf.LOG_INTERVAL * 60000 # number of ms to log readings
    # accumulate reading values that will be averaged
    # record number from the last time the system restarted
    sequence = 1
    counter = 0  # numbe of readings taken used for averaging
    recordNumber = 1  # record number restart when program restarts
    curr_time = rtc.datetime()

   # handle the logging in minutes
    cur_minutes = curr_time[5]
    boundary = cur_minutes % conf.LOG_INTERVAL 
    last_boundary = boundary
    b_hit = (cur_minutes % conf.LOG_INTERVAL) == 0

    # handle the sensor reading in ms
    now = time.ticks_ms()
    readtime = time.ticks_add(now, interval) # take readings

    # create variable to do TC averages based
    myReadings = conf.readings
    # initialization for those values that need to be reset
    for key in myReadings.keys():
        myReadings[key][2] = 0.0 # position is cumulative temp value
        myReadings[key][3] = 0   # position is reading count for averaging
        myReadings[key][4] = 0.0 # position is cumulative internal temp value

    print(f"START OF WHILE {realtc.formatrtc(rtc.datetime())} readtime {readtime}")
    while True:
    
        # collect data at 0 or negative diff, readtime was hit
        if time.ticks_diff(readtime, time.ticks_ms()) <= 0:
            now = time.ticks_ms()
            readtime = time.ticks_add(now, interval)

            # read TC values
            # readings = thermocouple.initReadings(conf.readings)
            # readings, myReadings = thermocouple.read_thermocouples(readings)
            # READ TC and add to myReadings, the accumulator for calculations
            for key in conf.readings.keys():
                cs_pin = conf.readings[key][0] # first position is pin number
                temperature, internal_temperature = thermocouple.read_thermocouple(cs_pin, tspi)

                if not math.isnan(temperature): # only increment true values and ignore nan values
                    myReadings[key][2] += temperature
                    myReadings[key][3] += 1
                    myReadings[key][4] += internal_temperature

            counter += 1
            print(f"added TC readings ot myReadings {counter}")
            gc.collect()    


        # LOG THE DATA AS NEEDED
        if (b_hit == True) and (counter > 0):
            print(f"***\nboundary hit, log: {realtc.formatrtc(curr_time)}, rtc time {realtc.formatrtc(rtc.datetime())}")
            print(f"##### BREAK TO LOG DATA #####")
            date_time = realtc.formatrtc(curr_time) # use the trigger time, not current time
            
            print(f"NEED TO LOG DATA: {date_time} interval: {interval}")
            
            # average out all of the readings for logging
            for key in myReadings.keys():
                if myReadings[key][3] > 0:  #  position 3 is number of successful reads for averaging
                    avgReading = round(myReadings[key][2] / myReadings[key][3], 2)
                    avgInternalReading = round(myReadings[key][4] / myReadings[key][3], 2)
                    # calReading = callibrated_re?eading(myReadings[key][3], avgReading)
                    # print(f"data key: {myReadings[key][3]}   key: {key}   avg: {avgReading}   cal: {calReading}")
                    conf.readings[key][2] = avgReading
                    conf.readings[key][4] = avgInternalReading
                else: # we didn't take any readings, therefore not a number
                    conf.readings[key][2] = float("NaN")
                    conf.readings[key][4] = float("NaN")

                temperature_data, internal_data = thermocouple.allReadings(conf.readings)
                # org_data, org_inter = thermocouple.allReadings(myReadings)
                gc.collect()

                out = ','.join([str(recordNumber), date_time, MY_ID, temperature_data, internal_data])
                # print(f"Data Packet: {out}")
                # transmit to all conf DATA_LOGGER values
                out = "TRC:" + out
                [espnowex.esp_tx(logger, esp_con, out) for logger in conf.peers['DATA_LOGGER']]
                sequence += 1
                gc.collect()

            recordNumber += 1              
            print(f"##### LOGGED DATA #####")

            # re-initialize variables
 
            # create variable to do averages based on readings structure
            myReadings = conf.readings
            # initialization for those values that need to be reset
            for key in myReadings.keys():
                myReadings[key][2] = 0.0 # position is cumulative temp value
                myReadings[key][3] = 0   # position is reading count for averaging
                myReadings[key][4] = 0.0 # position is cumulative internal temp value


            # TEMPERATURE CONTROL
            diff = conf.readings['TREATMENT'][2] - conf.readings['CONTROL'][2]
            # print(f"CHECK TEMP DIFFERENCE - cont:{readings['CONTROL'][2]}, heat:{readings['TREATMENT'][2]}, DIFFERENCE: {diff}")
            if math.isnan(diff) is True:
                D8.off()  # trouble reading sensor, turn off for safety TODO generate error in system log
            elif conf.readings['HEAT'][2] >= conf.TMAX_HEATER:  # error state, shut down heater
                D8.off()  # TODO record an ERROR in the system log
            elif conf.readings['TREATMENT'][2] >= conf.TMAX:  # warning leaf temp exceeded threshold, turn off heater
                D8.off()  # TODO record a WARNING in the system log
            # TODO there needs to be a deadband to prevent oscillation
            elif diff < (conf.TDIFF + 0.25):  # lower than required temp above control leaf
                D8.on()
            elif diff >= (conf.TDIFF - 0.25):  # higher than required temp control leaf
                D8.off()

            # get the accurate time, not sync, can be off by quite a bit
            realtc.get_remote_time(esp_con)
            print(f"RESET TIME: {realtc.formatrtc(rtc.datetime())}")
            gc.collect()
            # we logged for this boundary, skip until next boundary
            b_hit = False
        else:
            curr_time = rtc.datetime()
            cur_minutes = curr_time[5]
            boundary = cur_minutes % conf.LOG_INTERVAL 
            if boundary == last_boundary:
                print(f"{realtc.formatrtc(curr_time)} SKIP on {boundary} == {last_boundary}")
            else:
                b_hit = (cur_minutes % conf.LOG_INTERVAL) == 0
                last_boundary = boundary
                print(f"---{realtc.formatrtc(curr_time)} RESET to {boundary} == {last_boundary}")


        # conf.SAMPLE_INTERVAL
        time.sleep_ms(int(conf.SAMPLE_INTERVAL/3))
        # time.sleep(1) # don't run continuously
        print(f"LOOP FINISHED counter:{counter}, record number:{recordNumber}, read_ticks_ms:{time.ticks_diff(readtime, time.ticks_ms())}")
        # print(f"read:{time.ticks_diff(readtime, time.ticks_ms())}")

        gc.collect()


# ########################################################





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
