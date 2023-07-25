import time
import realtc
import BME280
import espnowex
import conf
import machine
import sys

def main():
    print("START SENSOR")


    # turn off WiFi and initalize the ESPNow protocol
    STATION, AP = espnowex.wifi_reset()
    ESP_CON = espnowex.init_esp_connection(STATION)

    RAW_MAC = espnowex.get_mac(STATION)
    # convert hex into readable mac address
    MY_MAC = ":".join(["{:02x}".format(b) for b in RAW_MAC])
    print(f"My MAC addres:: {MY_MAC} raw MAC:: {RAW_MAC}")

    # set the time from the logger
    retries = 0
    host = ""
    # espnowex.esp_tx(b'\xc4[\xbe\xe4\xfe=', ESP_CON, 'get_time')
    espnowex.esp_tx(conf.peers["DATA_LOGGER"], ESP_CON, "get_time")

    host, msg = espnowex.esp_rx(ESP_CON)

    while not msg:
        retries += 1
        espnowex.esp_tx(b"\xc4[\xbe\xe4\xfe=", ESP_CON, "get_time")
        # print("Time Sensor: wait for time response")
        host, msg = espnowex.esp_rx(ESP_CON)
        print(f"found host: {host}")
        print(f"Get Time: unable to get time ({retries})")
        time.sleep(3)

    print(host)
    str_host = ":".join(["{:02x}".format(b) for b in host])
    # assumption data is utf-8, if not, it may fail
    str_msg = msg.decode("utf-8")

    print("------------------------")
    print(f"received a respons from {host} {str_host} of: {msg}")
    et = eval(msg)
    print("--------------------")
    print(f"et: {et}")
    print("--------------------")

    rtc = machine.RTC()
    rtc.datetime(et)
    print(f"The new time is: {realtc.formattime(time.localtime())}")


    # ESP32 - Pin assignment
    # i2c = I2C(scl=Pin(22), sda=Pin(21), freq=10000)
    # ESP8266 - Pin assignment
    i2c = machine.I2C(scl=machine.Pin(5), sda=machine.Pin(4), freq=10000)

    print("i2c INITIALZED")

    recordNumber = 1  # record number from the last time the system restarted

    BM280_SENSOR = BME280.BME280(i2c=i2c)
    time.sleep(0.250)
    INTERVAL = conf.AVG_INTERVAL * 60  # number seconds to average readings
    # accumulate reading values that will be averaged
    temperature = 0.0
    humidity = 0.0
    pressure = 0.0
    counter = 0  # numbe of readings taken used for averaging
    temptimer = 0 # TODO this needs converted to a timer
    while True:
        temperature += float(BM280_SENSOR.temperature)
        humidity += float(BM280_SENSOR.humidity)
        pressure += float(BM280_SENSOR.pressure)
        counter += 1
        # Message = f'{temperature}, {humidity}, {Pressure}'
        # Message = ','.join([temperature, humidity, Pressure])
        date_time = realtc.formattime(time.localtime())
        out = ",".join(
        [str(recordNumber), MY_MAC, date_time, str(temperature), str(humidity), str(pressure)]
        )
        print(out)
        # espnowex.esp_tx(b'\xc4[\xbe\xe4\xfe=', ESP_CON, out)
        espnowex.esp_tx(conf.peers["DATA_LOGGER"], ESP_CON, out)
        recordNumber += 1

        time.sleep(30)
        temptimer += 30
        if temptimer == INTERVAL:
            # TODO this needs changed into proper math for read interval, avg interval
            temperature = temperature / (INTERVAL/30)
            humidity = humidity / (INTERVAL/30)
            pressure = pressure / (INTERVAL/30)
            date_time = realtc.formattime(time.localtime())
            out = ",".join(
            ["15 MINUTE AVERAGE: ", str(recordNumber), MY_MAC, date_time, str(temperature), str(humidity), str(pressure)]
            )
            print(out)
            # espnowex.esp_tx(b'\xc4[\xbe\xe4\xfe=', ESP_CON, out)
            espnowex.esp_tx(conf.peers["DATA_LOGGER"], ESP_CON, out)
            temperature = 0.0
            humidity = 0.0
            pressure = 0.0


if __name__ == "__main__":
    try:
        print(f"reset code: {machine.reset_cause()}")
        main()
    except KeyboardInterrupt as e:
        print(f"Got ctrl-c {e}")
        sys.exit()  # TODO this falls through and resets???? okay for now
    finally:
        print(f"Fatal error, restarting.  {machine.reset_cause()}")
        machine.reset()
