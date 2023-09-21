import time
import sys
import machine
import realtc
import BME280
import espnowex
import conf


def task(temperature, humidity, pressure, counter):
    print(f"task() run at: {realtc.formattime(time.localtime())}")
    # time.sleep(random.getrandbits(4)) # arbitrary time to complete testing
    temperature += float(BM280_SENSOR.temperature)
    humidity += float(BM280_SENSOR.humidity)
    pressure += float(BM280_SENSOR.pressure)
    counter += 1
    gc.collect()
    return temperature, humidity, pressure, counter

def log_data(esp_con, tsec, interval, boundary, recordNumber, MY_MAC):
    print("\n\n=============== LOG_DATA ===================")
    print(f"---------- {realtc.formattime(time.localtime())} ----------\n")
    out = "SYSLOG:" + ",".join([realtc.formattime(time.localtime()), realtc.formattime(time.localtime())[:-3], "LOGGING TEST", str(tsec), str(interval), str(boundary)])
    [espnowex.esp_tx(logger, esp_con, out) for logger in conf.peers['DATA_LOGGER']]
    print(f"\n---------- {realtc.formattime(time.localtime())} ----------")
    print("=============== END =========================\n\n")
    recordNumber += 1
    gc.collect()
    return recordNumber

def run(esp_con):
    # 15 minutes at (00, 15, 30, 45), value has to be in seconds, 
    # AVG_INTERVAL can be changed in the conf file to get other boundaries
    interval = conf.AVG_INTERVAL * 60 
    # counter = 0
    recordNumber = 1

    temperature, humidity, pressure, counter= intAccumulators(temperature, humidity, pressure, counter)

    while True:
        # run one task before checking the interval in the loop
        temperature, humidity, pressure, counter = task(temperature, humidity, pressure, counter)

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
            temperature, humidity, pressure, counter = task(temperature, humidity, pressure, counter) # run the task until interval is hit

            curr_time = rtc.datetime()
            tsec = ((curr_time[5] * 60) + curr_time[6])
            boundary = tsec % interval
            if boundary > last_boundary:
                last_boundary = boundary


        # interval was exceeded, run alternate code
        # send data to data logger
        print(f"NEED TO LOG DATA: {realtc.formattime(time.localtime())}  tsec:{tsec}  boundary %:{boundary}  last boundary: {last_boundary}  interval:{interval}")
        recordNumber = log_data(esp_con, tsec, interval, boundary, recordNumber, MY_MAC)
        
        # reset interval checking
        realtc.get_remote_time(esp_con)
        curr_time = rtc.datetime()
        tsec = ((curr_time[5] * 60) + curr_time[6])
        boundary = tsec % interval
        last_boundary = boundary

        temperature, humidity, pressure, counter= intAccumulators(temperature, humidity, pressure, counter)

        print(f"     RESET THE TIME: {realtc.formattime(time.localtime())}  tsec:{tsec}  boundary %:{boundary}  last boundary: {last_boundary}  interval:{interval}")

def intAccumulators(temperature, humidity, pressure, counter):
    temperature = 0.0
    humidity = 0.0
    pressure = 0.0
    counter = 0
    return temperature, humidity, pressure, counter


def set_clock(esp_con):

    # blocking: set the time from the logger
    retries = 0  # visual display on number of retries
    host = ""
    espnowex.esp_tx(conf.peers["DATA_LOGGER"], esp_con, "get_time")
    host, msg = espnowex.esp_rx(esp_con)
    while not msg:
        retries += 1
        espnowex.esp_tx(conf.peers["DATA_LOGGER"], esp_con, "get_time")
        # print("Time Sensor: wait for time response")
        host, msg = espnowex.esp_rx(esp_con)
        print(f"found host: {host}")
        print(f"Get Time: unable to get time ({retries})")
        time.sleep(3)

    str_host = ":".join(["{:02x}".format(b) for b in host])
    # assumption data is utf-8, if not, it may fail
    str_msg = msg.decode("utf-8")

    print("------------------------")
    print(f"received a respons from {host} {str_host} of: {str_msg}")
    et = eval(msg)
    # print("--------------------")
    # print(f"et: {et}")
    # print("--------------------")

    rtc = machine.RTC()
    rtc.datetime(et)
    print(f"The new time is: {realtc.formattime(time.localtime())}")


def main(esp_con, RAW_MAC):
    print("START SENSOR")

    # # turn off WiFi and initalize the ESPNow protocol
    # STATION, AP = espnowex.wifi_reset()
    # esp_con = espnowex.init_esp_connection(STATION)

    # RAW_MAC = espnowex.get_mac(STATION)
    # # convert hex into readable mac address
    MY_MAC = ":".join(["{:02x}".format(b) for b in RAW_MAC])
    print(f"My MAC addres:: {MY_MAC} RAW MAC:: {RAW_MAC}")

    set_clock(esp_con)
    time.sleep(5)  # give delay for reading output, not required

    # ESP8266 I2C setup pins
    i2c = machine.I2C(scl=machine.Pin(5), sda=machine.Pin(4), freq=10000)
    print("i2c INITIALZED")
    BM280_SENSOR = BME280.BME280(i2c=i2c)

    # INTERVAL = conf.AVG_INTERVAL * 60  # number seconds to average readings
    # accumulate reading values that will be averaged
    # temperature, humidity, pressure = intAccumulators(temperature, humidity, pressure)
    # counter = 0  # numbe of readings taken used for averaging
    # temptimer = 0  # TODO this needs converted to a timer
    recordNumber = 1  # record number from the last time the system restarted
    
    # ######################################## 
    while True:
        temperature += float(BM280_SENSOR.temperature)
        humidity += float(BM280_SENSOR.humidity)
        pressure += float(BM280_SENSOR.pressure)
        counter += 1


        time.sleep(30) # TODO add in power saving code
        temptimer += 30 # TODO this needs be a real timer
        if temptimer == INTERVAL:
            # TODO this needs changed into proper math for read interval, avg interval
            temptimer = 0
            temperature = temperature / (INTERVAL / 30)
            humidity = humidity / (INTERVAL / 30)
            pressure = pressure / (INTERVAL / 30)
            date_time = realtc.formattime(time.localtime())
            out = ",".join(
                [
                    str(recordNumber),
                    date_time,
                    MY_MAC,
                    str(temperature),
                    str(humidity),
                    str(pressure),
                ]
            )
            print(f"{conf.AVG_INTERVAL} MINUTE AVERAGE: {out}")
            espnowex.esp_tx(conf.peers["DATA_LOGGER"], esp_con, out)
            recordNumber += 1
            temperature, humidity, pressure = intAccumulators(temperature, humidity, pressure)
# ######################################## 

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
