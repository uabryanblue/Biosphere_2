import sys
import time
from math import isnan
import machine
import conf
import realtc
import thermocouple
import espnowex


def trc_main():
    print("START TEMPERATURE SENSOR")

    # relay control, start in the off state
    D8 = machine.Pin(15, machine.Pin.OUT)
    D8.off()

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
    str_host = ':'.join(['{:02x}'.format(b) for b in host]).upper()
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
        temperature_data, internal_data = thermocouple.allReadings(readings)
        org_data, org_inter = thermocouple.allReadings(myReadings)
        date_time, _, _ = realtc.formattime(time.localtime())
        out = ','.join([str(sequence), date_time, str_host, temperature_data, internal_data])
        print(out)
        espnowex.esp_tx(esp_con, out)
        sequence += 1
        # difference between treatment and control leaf handling
        # also check for heater going out of randge
        # and if temperature above maximum value for heating due to other reasons.
        diff = readings['TREATMENT'][2] - readings['CONTROL'][2]
        # print(f"CHECK TEMP DIFFERENCE - cont:{readings['CONTROL'][2]}, heat:{readings['TREATMENT'][2]}, DIFFERENCE: {diff}")
        
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

        time.sleep(5)

# if __name__ == "__main__":
#     try:
#         print(f'reset code: {machine.reset_cause()}')
#         main()
#     except KeyboardInterrupt as e:
#         print(f'Got ctrl-c {e}')
#         D8.off()
#         sys.exit() # TODO this falls through and resets???? okay for now
#     finally: 
#         print(f'Fatal error, restarting.  {machine.reset_cause()}')
#         D8.off()
#         machine.reset()





