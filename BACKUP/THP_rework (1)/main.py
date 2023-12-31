import gc
import micropython
gc.collect()
micropython.mem_info()
import BME280
gc.collect()
micropython.mem_info()

import time
import sys
import machine
import realtc
gc.collect()
micropython.mem_info()
import espnowex
import conf
gc.collect()
micropython.mem_info()

def set_clock(esp_con):

    # blocking: set the time from the logger
    retries = 0  # visual display on number of retries
    host = ""
    espnowex.esp_tx(conf.peers["TIME"][0], esp_con, "GET_TIME")
    gc.collect()
    host, msg = espnowex.esp_rx(esp_con)
    while not msg:
        retries += 1
        espnowex.esp_tx(conf.peers["TIME"][0], esp_con, "GET_TIME")
        gc.collect()
        host, msg = espnowex.esp_rx(esp_con)
        print(f"Get Time: unable to get time {host} ({retries})")
        time.sleep(3)

    str_host = ":".join(["{:02x}".format(b) for b in host])
    # assumption data is utf-8, if not, it may fail
    str_msg = msg.decode("utf-8")

    print(f"received a respons from {host} {str_host} of: {str_msg}")
    et = eval(msg)
    rtc = machine.RTC()
    rtc.datetime(et)
    print(f"The new time is: {realtc.formattime(time.localtime())}")

def main():
    print("START SENSOR")
    rtc = machine.RTC()

    station, ap = espnowex.wifi_reset()
    gc.collect()
    esp_con = espnowex.init_esp_connection(station)
    gc.collect()
    RAW_MAC = espnowex.get_mac(station)
    gc.collect()

    # convert hex into readable mac address
    MY_MAC = ":".join(["{:02x}".format(b) for b in RAW_MAC])
    print(f"My MAC addres:: {MY_MAC} RAW MAC:: {RAW_MAC}")

    set_clock(esp_con)

    # ESP8266 I2C setup pins
    i2c = machine.I2C(scl=machine.Pin(5), sda=machine.Pin(4), freq=10000)
    print("i2c INITIALZED")
    BM280_SENSOR = BME280.BME280(i2c=i2c)
    gc.collect()

    interval = conf.AVG_INTERVAL * 60  # number seconds to average readings
    # accumulate reading values that will be averaged
    temperature = 0.0
    humidity = 0.0
    pressure = 0.0
    counter = 0  # numbe of readings taken used for averaging
    recordNumber = 1  # record number from the last time the system restarted

    # run the task
    temperature += float(BM280_SENSOR.temperature)
    humidity += float(BM280_SENSOR.humidity)
    pressure += float(BM280_SENSOR.pressure)
    counter += 1
    gc.collect()

    curr_time = rtc.datetime()
    tsec = ((curr_time[5] * 60) + curr_time[6])
    boundary =  tsec % interval
    last_boundary = boundary
#
    while True:
    #     temperature += float(BM280_SENSOR.temperature)
    #     humidity += float(BM280_SENSOR.humidity)
    #     pressure += float(BM280_SENSOR.pressure)
    #     counter += 1
    #     gc.collect()

    #     # if the boundary happens to hit 0, or we have not gone over the interval run the task
    #     print(f"     BEFORE WHILE: {realtc.formattime(time.localtime())}  tsec:{tsec}  boundary %:{boundary}  last boundary: {last_boundary}  interval:{interval}")
    #     while (last_boundary == boundary): # case == 0 very rare, look at exceeding only
    #         print(f"LOOP ----- {realtc.formattime(time.localtime())}  tsec:{tsec}  boundary %:{boundary}  last boundary: {last_boundary}  interval:{interval}")
            
    #         # run the task
    #         temperature += float(BM280_SENSOR.temperature)
    #         humidity += float(BM280_SENSOR.humidity)
    #         pressure += float(BM280_SENSOR.pressure)
    #         counter += 1
    #         gc.collect()

    #         curr_time = rtc.datetime()
    #         tsec = ((curr_time[5] * 60) + curr_time[6])
    #         boundary = tsec % interval
    #         if boundary > last_boundary:
    #             last_boundary = boundary

        # # interval was exceeded, run alternate code
        # # send data to data logger
        # print(f"NEED TO LOG DATA: {realtc.formattime(time.localtime())}  tsec:{tsec}  boundary %:{boundary}  last boundary: {last_boundary}  interval:{interval}")
        # date_time = realtc.formattime(time.localtime())
        # out = ",".join([str(recordNumber), date_time, MY_MAC, str(temperature), str(humidity), str(pressure)])
        # out = "CLIMATE:" + out
        # print(f"{conf.AVG_INTERVAL} MINUTE AVERAGE: {out}")
        # [espnowex.esp_tx(logger, esp_con, out) for logger in conf.peers['DATA_LOGGER']]
        # out = ""
        gc.collect()

        # # reset interval checking
        # realtc.get_remote_time(esp_con)
        # curr_time = rtc.datetime()
        # tsec = ((curr_time[5] * 60) + curr_time[6])
        # boundary = tsec % interval
        # last_boundary = boundary
        # print(f"     RESET THE TIME: {realtc.formattime(time.localtime())}  tsec:{tsec}  boundary %:{boundary}  last boundary: {last_boundary}  interval:{interval}")

        recordNumber += 1
        counter = 0
        temperature = 0.0
        humidity = 0.0
        pressure = 0.0

        gc.collect()

if __name__ == "__main__":
    try:
        print(f"reset code: {machine.reset_cause()}")
        main()
    except KeyboardInterrupt as e:
        print(f"received ctrl-c {e}")
        sys.exit()  # this allows a double ctrl-c to stop all execution without restart
    finally:
        print(f"Fatal error, restarting.  {machine.reset_cause()}")
        machine.reset()
