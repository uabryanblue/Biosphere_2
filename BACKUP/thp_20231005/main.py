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

# def set_clock(esp_con):

#     # blocking: set the time from the logger
#     retries = 0  # visual display on number of retries
#     host = ""
#     espnowex.esp_tx(conf.peers["TIME"][0], esp_con, "GET_TIME")
#     gc.collect()
#     host, msg = espnowex.esp_rx(esp_con)
#     while not msg:
#         retries += 1
#         espnowex.esp_tx(conf.peers["TIME"][0], esp_con, "GET_TIME")
#         gc.collect()
#         host, msg = espnowex.esp_rx(esp_con)
#         print(f"Get Time: unable to get time {host} ({retries})")
#         time.sleep(1)

#     str_host = ":".join(["{:02x}".format(b) for b in host])
#     # assumption data is utf-8, if not, it may fail
#     str_msg = msg.decode("utf-8")

#     print(f"received a respons from {host} {str_host} of: {str_msg}")
#     et = eval(msg)
#     rtc = machine.RTC()
#     rtc.datetime(et)
#     print(f"The new time is: {realtc.formattime(time.localtime())}")

def main():
    print("START SENSOR")
    rtc = machine.RTC()

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
        # TODO send an error message recorded in the datalogger syslog

    # turn off WiFi and init espnow
    station, ap = espnowex.wifi_reset()
    gc.collect()
    esp_con = espnowex.init_esp_connection(station)
    gc.collect()
    RAW_MAC = espnowex.get_mac(station)
    gc.collect()

    # convert hex into readable mac address
    MY_MAC = ":".join(["{:02x}".format(b) for b in RAW_MAC])
    print(f"My MAC addres:: {MY_MAC} RAW MAC:: {RAW_MAC}")
    
    # set_clock(esp_con)
    realtc.get_remote_time(esp_con)
    gc.collect()

    # BME280 setup on I2C
    i2c = machine.I2C(scl=machine.Pin(5), sda=machine.Pin(4), freq=10000)
    BME280_SENSOR = BME280.BME280(i2c=i2c)
    print("BME280 i2c INITIALZED")
    gc.collect()

    # initialize variables
    interval = conf.AVG_INTERVAL * 60  # number seconds to average readings
    # accumulate reading values that will be averaged
    temperature = 0.0
    humidity = 0.0
    pressure = 0.0
    counter = 0  # numbe of readings taken used for averaging
    recordNumber = 1  # record number from the last time the system restarted

    # # run the task
    # temperature += float(BME280_SENSOR.temperature)
    # humidity += float(BME280_SENSOR.humidity)
    # pressure += float(BME280_SENSOR.pressure)
    # counter += 1
    # gc.collect()

    curr_time = rtc.datetime()
    tsec = ((curr_time[5] * 60) + curr_time[6])
    boundary = tsec % interval
    last_boundary = boundary

    while True:
        # collect data
        temperature += float(BME280_SENSOR.temperature)
        humidity += float(BME280_SENSOR.humidity)
        pressure += float(BME280_SENSOR.pressure)
        counter += 1
        gc.collect()

        # if the boundary happens to hit 0, or we have not gone over the interval run the task
        print(f"BEFORE WHILE: {realtc.formatrtc(curr_time)}  tsec:{tsec}  boundary %:{boundary}  last boundary: {last_boundary}  interval:{interval}")
        while (last_boundary == boundary): # set equal below to trigger logging at the correct time
            # get values every 5 seconds
            time.sleep(5)
            # run the task
            temperature += float(BME280_SENSOR.temperature)
            humidity += float(BME280_SENSOR.humidity)
            pressure += float(BME280_SENSOR.pressure)
            counter += 1
            gc.collect()

            curr_time = rtc.datetime()
            tsec = ((curr_time[5] * 60) + curr_time[6]) # minutes * 60 + seconds
            boundary = tsec % interval # mod the total elapsed seconds by interval in seconds
            print(f'------- tsec {tsec}, boundary% {boundary}, last_boundary {last_boundary}, counter {counter}')
            if boundary > last_boundary and counter <= interval: 
                # print(f'### continue {boundary} > {last_boundary} and {counter} <= {interval}')
                last_boundary = boundary

        # interval was exceeded, run alternate code
        # send data to data logger
        # date_time = realtc.formattime(time.localtime())
        print(f'\n### BREAK {boundary} > {last_boundary} and {counter} <= {interval}\n')

        date_time = realtc.formatrtc(curr_time)
        # are time and rtc the same? should be as just reset
        tm = realtc.formattime(time.localtime())
        rtm = realtc.formatrtc(rtc.datetime())
        print(f"NEED TO LOG DATA: {date_time}, tm: {tm}, rtm: {rtm},\n  tsec: {tsec},  boundary %: {boundary},  last boundary: {last_boundary}, interval: {interval}")
        out = ",".join([str(recordNumber), date_time, MY_MAC, str(temperature/counter), str(humidity/counter), str(pressure/counter), str(counter)])
        out = "CLIMATE:" + out
        print(f"{conf.AVG_INTERVAL} MINUTE AVERAGE: {out}")
        [espnowex.esp_tx(logger, esp_con, out) for logger in conf.peers['DATA_LOGGER']]

        # re-initialize variables
        del date_time
        del out
        del tm
        del rtm
        recordNumber += 1
        counter = 0
        temperature = 0.0
        humidity = 0.0
        pressure = 0.0
        gc.collect()


        realtc.get_remote_time(esp_con)
        curr_time = rtc.datetime()
        tsec = ((curr_time[5] * 60) + curr_time[6])
        boundary = tsec % interval
        last_boundary = boundary        # reset interval checking
        print(f"RESET THE TIME: {realtc.formatrtc(curr_time)}, tsec:{tsec}  boundary %:{boundary}  last boundary: {last_boundary} interval:{interval}")

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
