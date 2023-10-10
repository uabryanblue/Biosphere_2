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
    STR_MAC = "".join(["{:02x}".format(b) for b in RAW_MAC])
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
    recordNumber = 1  # record number from the last time the system restarted


    # now = time.ticks_ms(); deadline = time.ticks_add(time.ticks_ms(), 5000)
    # if time.ticks_diff(deadline, time.ticks_ms()) <= 0:
    #     do_a_little_of_something()
    # now = time.ticks_ms(); deadline = time.ticks_add(time.ticks_ms(), 5000)

    # # This code snippet is not optimized docs.micropython.org
    # now = time.ticks_ms()
    # scheduled_time = task.scheduled_time()
    # if ticks_diff(scheduled_time, now) > 0:
    #     print("Too early, let's nap")
    #     sleep_ms(ticks_diff(scheduled_time, now))
    #     task.run()
    # elif ticks_diff(scheduled_time, now) == 0:
    #     print("Right at time!")
    #     task.run()
    # elif ticks_diff(scheduled_time, now) < 0:
    #     print("Oops, running late, tell task to run faster!")
    #     task.run(run_faster=true)

    rtc = machine.RTC()
    # curr_time = rtc.datetime()
    # tsec = ((curr_time[5] * 60) + curr_time[6])
    # boundary = tsec % interval
    # last_boundary = boundary
    # take a reading every 5 second using RTC clock

    now = time.ticks_ms()
    logtime  = time.ticks_add(now, log_interval) # log entries
    readtime = time.ticks_add(now, interval) # take readings
    print(f"STARE OF WHILE {realtc.formatrtc(rtc.datetime())} readtime {readtime}, logtime {logtime}")
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

        # log data at 0 or negative diff, logtime was hit
        if time.ticks_diff(logtime, time.ticks_ms()) <= 0:
            now = time.ticks_ms()
            logtime = time.ticks_add(now, log_interval)

            print(f"##### BREAK TO LOG DATA #####")
            date_time = realtc.formatrtc(rtc.datetime()) # curr_time from above
            # are time and rtc the same? should be as just reset
            # tm = realtc.formattime(time.localtime())
            # rtm = realtc.formatrtc(rtc.datetime())
            print(f"NEED TO LOG DATA: {date_time} interval: {interval}")
            out = ",".join([str(recordNumber), date_time, STR_MAC, str(temperature/counter), str(humidity/counter), str(pressure/counter), str(counter)])
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
            # get the accurate time, not sync, can be off by quite a bit
            realtc.get_remote_time(esp_con)
            print(f"RESET TIME: {realtc.formatrtc(rtc.datetime())}")
            gc.collect()

        time.sleep(1) # don't run continuously
        print(f"LOOP FINISHED counter:{counter}, record number:{recordNumber}")
        print(f"read:{time.ticks_diff(readtime, time.ticks_ms())} log:{time.ticks_diff(logtime, time.ticks_ms())}")

        gc.collect()

if __name__ == "__main__":
    try:
        print(f"reset code: {machine.reset_cause()}")
        main()
    except KeyboardInterrupt as e:
        print(f"Got ctrl-c {e}")
    finally:
        print(f"Fatal error, restarting.  {machine.reset_cause()} !!!!!!!!!!!")
        machine.reset()