import machine
import time

# import logger
import conf
from math import isnan
import realtc
# import sd
import thermocouple
import espnowex
import sys


print("START TEMPERATURE SENSOR")

# relay control, start in the off state
D8 = machine.Pin(15, machine.Pin.OUT)
D8.off()

def main():

    # con = espnowex.init_esp_connection()
    sta, ap = espnowex.wifi_reset()
    esp_con = espnowex.init_esp_connection(sta)


    # convert hex into readable mac address
    RAW_MAC = espnowex.get_mac(sta)
    MY_MAC = ':'.join(['{:02x}'.format(b) for b in RAW_MAC])
    # print(f"My MAC:: {MY_MAC}")
    print(f"My MAC addres:: {MY_MAC} raw MAC:: {RAW_MAC}")

    # set the time from the logger
    retries = 0
    host = ''
    espnowex.esp_tx(esp_con, 'get_time')
    host, msg = espnowex.esp_rx(esp_con)

    while not msg:
        retries += 1
        espnowex.esp_tx(esp_con, 'get_time')
        # print("Time Sensor: wait for time response")
        host, msg = espnowex.esp_rx(esp_con)
        print(f'found host: {host}')        
        print(f"Get Time: unable to get time ({retries})")
        time.sleep(3)

    print(host)
    str_host = ':'.join(['{:02x}'.format(b) for b in host])
    # assumption data is utf-8, if not, it may fail
    str_msg = msg.decode('utf-8')

    print("------------------------")
    print(f"received a respons from {host} {str_host} of: {msg}") 
    et = eval(msg)
    print("--------------------")
    print(f"et: {et}")
    print("--------------------")

    rtc = machine.RTC()
    rtc.datetime(et)
    print(f"Temp Sensor: the new time is: {realtc.formattime(time.localtime())}")  

    sequence = 1 # record number from the last time the system restarted

    while True:
        readings = thermocouple.initReadings(conf.readings)
        readings, myReadings = thermocouple.read_thermocouples(readings)

    
        # temperature_data = ', '.join([str(value[2]) for value in readings.values()])
        temperature_data = thermocouple.allReadings(readings)
        org_data = thermocouple.allReadings(myReadings)
        date_time = realtc.formattime(time.localtime())
        out = str(sequence) + ', ' + date_time + ', ' + temperature_data
        print(out)
        espnowex.esp_tx(esp_con, out)

        # difference between treatment and control leaf handling
        # also check for heater going out of randge
        # and if temperature above maximum value for heating due to other reasons.
        diff = readings['TREATMENT'][2] - readings['CONTROL'][2]
        print(f"CHECK TEMP DIFFERENCE - cont:{readings['CONTROL'][2]}, heat:{readings['TREATMENT'][2]}, DIFFERENCE: {diff}")
        
        if isnan(diff) is True:
            D8.off() # trouble reading sensor, turn off for safety TODO generate error in system log
        elif readings['HEATER'][2] >= conf.TMAX_HEATER: # error state, shut down heater
            D8.off() # TODO record an ERROR in the system log
        elif readings['TREATMENT'][2] >= conf.TMAX: # warning leaf temp exceeded threshold, turn off heater
            D8.off() # TODO record a WARNING in the system log
        # TODO there needs to be a deadband to prevent oscillation
        elif diff < (conf.TDIFF + 0.25): # lower than required temp above control leaf
            D8.on() 
        elif diff >= (conf.TDIFF - 0.25): # higher than required temp control leaf
            D8.off()


        # if diff <= 4.75:
        #     print("diff <= 4.5, D8 is on")
        #     D8.on()
        # elif diff > 4.75 or diff == 'nan':
        #     print("diff >= 4.75 D8 is off")
        #     D8.off()
        sequence += 1
        time.sleep(5)

if __name__ == "__main__":
    try:
        print(f'rest code: {machine.reset_cause()}')
        main()
    except KeyboardInterrupt as e:
        print(f'Got ctrl-c {e}')
        D8.off()
        sys.exit() # TODO this falls through and resets???? okay for now
    finally: 
        print(f'Got another error and exiting  {machine.reset_cause()}')
        D8.off()
        machine.reset()





