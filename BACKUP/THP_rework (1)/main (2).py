import time
import sys
import machine
import realtc
import BME280
import espnowex
import conf
import gc

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

def init_device():

    # turn off wifi and connect with ESPNow
    station, ap = espnowex.wifi_reset()
    gc.collect()
    esp_con = espnowex.init_esp_connection(station)
    gc.collect()

    # convert hex into readable mac address
    RAW_MAC = espnowex.get_mac(station)
    gc.collect()
    # MY_MAC = ":".join(["{:02x}".format(b) for b in RAW_MAC])
    # print(f"My MAC addres:: {MY_MAC} raw MAC:: {RAW_MAC}")

    return esp_con, station, RAW_MAC



def main():
    print("START SENSOR")

    # turn off WiFi and initalize the ESPNow protocol
    # station, AP = espnowex.wifi_reset()
    # esp_con = espnowex.init_esp_connection(station)
    # RAW_MAC = espnowex.get_mac(station)
    esp_con, station, RAW_MAC = init_device()
    gc.collect()
    # convert hex into readable mac address
    MY_MAC = ":".join(["{:02x}".format(b) for b in RAW_MAC])
    print(f"My MAC addres:: {MY_MAC} RAW MAC:: {RAW_MAC}")

    set_clock(esp_con)
    # time.sleep(5)  # give delay for reading output, not required

    # ESP8266 I2C setup pins
    i2c = machine.I2C(scl=machine.Pin(5), sda=machine.Pin(4), freq=10000)
    print("i2c INITIALZED")
    BM280_SENSOR = BME280.BME280(i2c=i2c)
    gc.collect()

    INTERVAL = conf.AVG_INTERVAL * 60  # number seconds to average readings
    # accumulate reading values that will be averaged
    temperature = 0.0
    humidity = 0.0
    pressure = 0.0
    counter = 0  # numbe of readings taken used for averaging
    temptimer = 0  # TODO this needs converted to a timer
    recordNumber = 1  # record number from the last time the system restarted
    
    while True:
        temperature += float(BM280_SENSOR.temperature)
        humidity += float(BM280_SENSOR.humidity)
        pressure += float(BM280_SENSOR.pressure)
        counter += 1
        gc.collect()


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
            out = "CLIMATE:" + out
            print(f"{conf.AVG_INTERVAL} MINUTE AVERAGE: {out}")

            # espnowex.esp_tx(conf.peers["DATA_LOGGER"], esp_con, out)
            [espnowex.esp_tx(logger, esp_con, out) for logger in conf.peers['DATA_LOGGER']]
            gc.collect()
            recordNumber += 1
            temperature = 0.0
            humidity = 0.0
            pressure = 0.0


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
