
import gc
import machine
gc.collect()
import time
import sys
gc.collect()
import math
import realtc
gc.collect()
import espnowex
gc.collect()
import thermocouple
import conf
gc.collect()

rtc = machine.RTC()

# visual 5 second led on startup
# status pin for logger, GPIO16/D0
D0 = machine.Pin(16, machine.Pin.OUT)
D0.off() # visual we started
# slow any restart loops
time.sleep(5)
D0.on() # turn off
del D0 

D8 = machine.Pin(15, machine.Pin.OUT)
D8.off() # TODO D8 HAS TO BE SET TO OFF ON ERROR !!!!!!!!!!!!!!!!!!
gc.collect()

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

def average_readings(myReadings):
    # average out all of the readings for logging

    for key in myReadings.keys():
        if myReadings[key][3] > 0:  #  position 3 is number of successful reads for averaging
            print(f"     AVERAGE  # reads {myReadings[key][3]}, temp: {myReadings[key][2]}")
            myReadings[key][2]  = round(myReadings[key][2] / myReadings[key][3], 2)
            myReadings[key][4] = round(myReadings[key][4] / myReadings[key][3], 2)
            # myReadings[key][3] = 1
            # calReading = callibrated_re?eading(myReadings[key][3], avgReading)
            # print(f"data key: {key}  num: {myReadings[key][3]}     avg: {avgReading}   cal: {calReading}")

        else: # we didn't take any readings, therefore not a number
            myReadings[key][2] = float("NaN")
            myReadings[key][4] = float("NaN")
        # print(myReadings)
    return myReadings

def update_heating(treatment_temp, reference_temp, heat_temp):

    if (treatment_temp * reference_temp) == 0:
        print(f"------------ERROR TURN RELAY OFF, 0 found! ref {reference_temp} or treat {treatment_temp} --------------")
        D8.off()
        return        
    diff = treatment_temp - reference_temp
    # diff = treatment_avg - reference_avg
    # on = conf.TDIFF * 0.01 # - 0.5)
    # off = conf.TDIFF - 0.75
    on = conf.TDIFF * 0.8
    off = conf.TDIFF * 1.05 
    # print(f"ON: {on}  OFF: {off}")

    # deadband to prevent oscillation
    # set relay based on delta T first, then look for out of range errors
    TurnOn = False
    # if diff <= (conf.TDIFF - 0.5):  # lower than required temp above control leaf
    if diff <= (off):  # lower than required temp above control leaf
        TurnOn = True
    elif diff > (on):  # higher than required temp control leaf
        TurnOn = False

    # check for out of bounds conditions
    ErrorTemp = False
    if math.isnan(diff) is True:
        ErrorTemp = ErrorTemp and True
    elif heat_temp >= conf.TMAX_HEATER:  # error state, shut down heater
        ErrorTemp = ErrorTemp and True
    elif treatment_temp >= conf.TMAX:  # warning leaf temp exceeded threshold, turn off heater
        ErrorTemp = ErrorTemp and True
    print(f"\n")
    if (TurnOn == True) and (ErrorTemp == False):
        print(f"***  ON ***       DIFF: {diff:<5}")
        D8.on()
    else:
        print(f"***  OFF ***      DIFF: {diff:<5}")
        D8.off()
    print(f"#----------------------------#")
    print(f"ON: <= {on:<5}  OFF: > {off:<5}\ntrt: {treatment_temp:5}  ref: {reference_temp:5}")
    print(f"#----------------------------#\n")


def main():
    print("--------START DEVICE--------")

    esp_con, station, RAW_MAC = init_device()

    # relay control, start in the off state
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

        # visual 3 second led on got remote time
        # status pin for logger, GPIO16/D0
        D0 = machine.Pin(16, machine.Pin.OUT)
        D0.off() # led on
        time.sleep(3)
        D0.on() # turn off
        del D0 

    else:
        print(f'MY ROLE IS {conf.MYROLE} BUT IT SHOULD BE "TRC".')
        print('!!!!!!!!invalid conf.py file!!!!!!!!')

# ########################################################
#               INITIALIZE TRC
# ########################################################

    # convert hex into readable mac address
    MY_MAC = ":".join(["{:02x}".format(b) for b in RAW_MAC])
    MY_ID = "".join(["{:02x}".format(b) for b in RAW_MAC]).upper()
    print(f"My MAC addres:: {MY_MAC} RAW MAC:: {RAW_MAC}")
    
    # sync date/time before starting
    realtc.get_remote_time(esp_con)
    gc.collect()

    # ----------  MACHINE SETUP
    tspi = machine.SPI(1, baudrate=5000000, polarity=0, phase=0)
    gc.collect()

    # initialize variables
    log_interval = conf.LOG_INTERVAL

    counter = 0  # number of readings taken, used for averaging
    recordNumber = 1  # restart causes reset of record number
    curr_time = rtc.datetime()

   # handle the logging in minutes
    cur_minutes = curr_time[5]
    boundary = cur_minutes % conf.LOG_INTERVAL 
    last_boundary = boundary
    b_hit = False # start in do not log state

    # handle the sensor reading in ms
    now = time.ticks_ms()
    readtime = time.ticks_add(now, 1) # trigger readings first things
    gc.collect()
    # create variable to do TC accumulation
    # myReadings = conf.readings
    myReadings = {}
    myReadings = thermocouple.createReadings(myReadings)
    # myReadings = thermocouple.initReadings(myReadings)
    gc.collect()

    # create variable to hold individual TC readings
    # avg_readings = conf.readings
    avg_readings = {}
    avg_readings = thermocouple.createReadings(avg_readings)

    # avg_readings = thermocouple.initReadings(avg_readings)

    # ########################################################
    #               START RUNNING TRC
    # ########################################################
    print(f"START OF WHILE {realtc.formatrtc(rtc.datetime())} readtime {readtime}\n")
    while True:
    
        # BEGIN SAMPLING LOOP
        # collect data when diff is <= 0, timer ran out
        if time.ticks_diff(readtime, time.ticks_ms()) <= 0:
            now = time.ticks_ms()
            readtime = time.ticks_add(now, conf.SAMPLE_INTERVAL)    
            # print(f"RESET TICKS {now}, {readtime}")
            # # TODO not working cal_readings = {}
            # read TC values
            avg_readings = thermocouple.initReadings(avg_readings)
            # print(f'\nMY  {myReadings}')
            # print(f'AVG {avg_readings}')
            avg_readings, cal_readings = thermocouple.readThermocouples(tspi) 
            # print(f'\nMY  {myReadings}')
            # print(f'AVG {avg_readings}\n')
            # make relay decisions for heating on current reading
            update_heating(avg_readings["TREATMENT"][2], avg_readings["REFERENCE"][2], avg_readings["HEAT"][2])
            # # TODO not working update_heating(cal_readings["TREATMENT"], cal_readings["REFERENCE"], cal_readings["HEAT"])

            for key in avg_readings.keys():
                # only increment if treatment has a non-error value, ignore all on nan values, or no reads
                if (not math.isnan(avg_readings[key][2])) and (avg_readings[key][3] > 0): 
                    # print(f"Before           key +1 {key} temp my-avg: {myReadings[key][2]} -- {avg_readings[key][2]} # reads:  my-avg {myReadings[key][3]} -- {avg_readings[key][3]}")
                    myReadings[key][2] += avg_readings[key][2]
                    myReadings[key][3] += 1 # avg_readings[key][3] should be 1 added each read
                    myReadings[key][4] += avg_readings[key][4]
                    # print(f"After            key +1 {key} temp: {myReadings[key][2]} -- {avg_readings[key][2]} # reads: {myReadings[key][3]} -- {avg_readings[key][3]}")
                else:
                    print(f"Bad TC reading. Key: {key:14} {avg_readings[key][2]:<4} cnt read: {avg_readings[key][3]:<4}")

            print(f"TC reading: {counter}\n")
            counter += 1
            gc.collect()    
        # END OF SAMPLING LOOP


        # ############### LOG THE DATA ############### 
        if (b_hit == True): 
            date_time = realtc.formatrtc(curr_time) # use the trigger time, not current time
            print(f"##### BREAK TO LOG DATA  {date_time}, rtc time {realtc.formatrtc(rtc.datetime())} log int (min): {conf.LOG_INTERVAL:4}")
            
            # print(f"log time: {date_time} log interval: {conf.LOG_INTERVAL} min")
            

            # ########## CALCULATE AVERAGES ########## 
            myReadings = average_readings(myReadings)
            # print(f"!!!!!!!!!!!!!!!!!!!!!!!!!! AVERAGED READINGS !!!!!!!!!!!!!!!!!!!!!!!!!!")
            # ########## FORMAT AND SEND DATA ########## 
            temperature_data, internal_data = thermocouple.allReadings(myReadings)
            # org_data, org_inter = thermocouple.allReadings(myReadings)
            gc.collect()
            out = ','.join([str(recordNumber), date_time, MY_ID, temperature_data, internal_data])
            # print(f"Data Packet: {out}")
            # transmit to all conf DATA_LOGGER values
            out = "TRC:" + out

            print(f"##### LOG DATA #####")
            [espnowex.esp_tx(logger, esp_con, out) for logger in conf.peers['DATA_LOGGER']]
            gc.collect()

            counter = 0
            recordNumber += 1              
            print(f"##### LOGGED DATA #####")

            # ########## RE-INIT VARIABLES ##########  
            # create variable to do averages based on readings structure
            myReadings = conf.readings
            myReadings = thermocouple.initReadings(myReadings)
            avg_readings = thermocouple.initReadings(avg_readings)

            if recordNumber % 20 == 0:
                # get the accurate time, not sync, can be off by quite a bit
                realtc.get_remote_time(esp_con)
                print(f"RESET TIME: {realtc.formatrtc(rtc.datetime())}")
                time.sleep(0.25)
                gc.collect()
            # we logged for this boundary, skip until next boundary
            b_hit = False
        else:
            # ########## NO LOGGING, SKIP ########## 
            curr_time = rtc.datetime()
            cur_minutes = curr_time[5]
            # print(f"boundary {boundary} and cur_minutes {cur_minutes}")
            boundary = cur_minutes % conf.LOG_INTERVAL 
            if boundary != last_boundary:
                b_hit = (cur_minutes % conf.LOG_INTERVAL) == 0
                last_boundary = boundary
            #     # print(f"---BREAK - break {b_hit}  {realtc.formatrtc(curr_time)} - {boundary:5} == {last_boundary:<5}")

            #     # print(f"SKIP - break {b_hit} {realtc.formatrtc(curr_time)} - {boundary:5} == {last_boundary:<5}")
            # else:
            #     b_hit = (cur_minutes % conf.LOG_INTERVAL) == 0
            #     last_boundary = boundary
            #     # print(f"---BREAK - break {b_hit}  {realtc.formatrtc(curr_time)} - {boundary:5} == {last_boundary:<5}")

        # don't run continuously
        # time.sleep_ms(int(conf.SAMPLE_INTERVAL/3))
        print(f"LOOP FINISHED {realtc.formatrtc(curr_time)} counter:{counter:4}, record number:{recordNumber:4}, read_ticks_ms:{time.ticks_diff(readtime, time.ticks_ms()):10}")

        gc.collect()

# ########################################################


if __name__ == "__main__":
    try:
        print(f"reset code: {machine.reset_cause()}")
        D8.off() 
        main() # give information on why there was a reset
    except KeyboardInterrupt as e:
        print(f"Received <CTRL> C {e}")
        D8.off() 
        # This falls through and resets, hit "<CTRL> C" 2 TIMES to get out
    finally:
        print(f"Fatal error, restarting.  {machine.reset_cause()}")
        D8.off()
        machine.reset()
