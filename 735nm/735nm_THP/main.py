# memory is an issue, imports need done in order, and gc collect performed
import gc
import micropython
gc.collect()
gc.threshold(gc.mem_free() // 4 + gc.mem_alloc())
micropython.mem_info()
import BME280
gc.collect()

import time
import machine
import realtc
gc.collect()
import espnowex
import conf
gc.collect()

# visual 5 second led on startup
# status pin for logger, GPIO16/D0
D0 = machine.Pin(16, machine.Pin.OUT)
D0.off() # visual we started
# slow any restart loops
time.sleep(5)
D0.on()
del D0

rtc = machine.RTC()

curr_time = rtc.datetime()


def main():
    print("START SENSOR")

    # verify that the conf.py file is associated with this code base
    if conf.MYROLE == "THP":
        print("\n================ MY CONFIGURATION ================")
        print("MY DATA LOGGERS")
        [print(val) for val in conf.peers['DATA_LOGGER']]
        print("MY TIME SERVER")
        [print(val) for val in conf.peers['TIME']]
        print("================ MY CONFIGURATION ================\n")
    else:
        print(f'MY ROLE IS {conf.MYROLE} BUT IT SHOULD BE "THP".')
        print('!!!!!!!!invalid conf.py file!!!!!!!!')

    # turn off WiFi and init espnow
    station, ap = espnowex.wifi_reset()
    gc.collect()
    esp_con = espnowex.init_esp_connection(station)
    gc.collect()
    RAW_MAC = espnowex.get_mac(station)
    gc.collect()

    # convert hex into readable mac address
    MY_MAC = ":".join(["{:02x}".format(b) for b in RAW_MAC])
    MY_ID = "".join(["{:02x}".format(b) for b in RAW_MAC]).upper()
    print(f"My MAC addres:: {MY_MAC} RAW MAC:: {RAW_MAC}")
    
    # sync date/time before starting
    realtc.get_remote_time(esp_con)
    gc.collect()

    # BME280 setup on I2C
    i2c = machine.I2C(scl=machine.Pin(5), sda=machine.Pin(4), freq=10000)
    gc.collect()
    print("starting BME280")
    BME280_SENSOR = BME280.BME280(i2c=i2c)
    print("BME280 i2c INITIALZED")
    gc.collect()

    # initialize variables
    interval = conf.SAMPLE_INTERVAL # number ms to average readings
    log_interval = conf.LOG_INTERVAL * 60000 # number of ms to log readings
    # accumulate reading values that will be averaged
    temperature = 0.0
    humidity = 0.0
    pressure = 0.0
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

    print(f"START OF WHILE {realtc.formatrtc(rtc.datetime())} readtime {readtime}")
    while True:
    
        # collect data at 0 or negative diff, readtime was hit
        if time.ticks_diff(readtime, time.ticks_ms()) <= 0:
            now = time.ticks_ms()
            readtime = time.ticks_add(now, interval)

            temperature += float(BME280_SENSOR.temperature)
            humidity += float(BME280_SENSOR.humidity)
            pressure += float(BME280_SENSOR.pressure)
            counter += 1
            print(f"added THP reading {counter}")
            gc.collect()    


        # LOG THE DATA AS NEEDED
        if (b_hit == True) and (counter > 0):
            print(f"***\nboundary hit, log: {realtc.formatrtc(curr_time)}, rtc time {realtc.formatrtc(rtc.datetime())}")
            print(f"##### BREAK TO LOG DATA #####")
            date_time = realtc.formatrtc(curr_time) # use the trigger time, not current time
            
            print(f"NEED TO LOG DATA: {date_time} interval: {interval}")
            out = ",".join([str(recordNumber), date_time, MY_ID, str(temperature/counter), str(humidity/counter), str(pressure/counter), str(counter)])
            out = "CLIMATE:" + out
            # print(f"LOG:{conf.AVG_INTERVAL} MINUTE AVERAGE: {out}")
            [espnowex.esp_tx(logger, esp_con, out) for logger in conf.peers['DATA_LOGGER']]
            print(f"##### LOGGED DATA #####")

            # re-initialize variables
            recordNumber += 1
            counter = 0
            temperature = 0.0
            humidity = 0.0
            pressure = 0.0

            if recordNumber % 4 == 0:
                # get the accurate time, not sync, can be off by quite a bit
                realtc.get_remote_time(esp_con)
                print(f"RESET TIME: {realtc.formatrtc(rtc.datetime())}")
                time.sleep(0.25)
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

if __name__ == "__main__":
    try:
        print(f"reset code: {machine.reset_cause()}")
        main()
    except KeyboardInterrupt as e:
        print(f"Got   ctrl-c {e}")
    finally:
        print(f"Fatal error, restarting.  {machine.reset_cause()} !!!!!!!!!!!")
        machine.reset()
