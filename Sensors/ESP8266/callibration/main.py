import sys
import time
from math import isnan
import machine

# import program configuration
import conf
import realtc
import thermocouple
import espnowex
# import callibrate


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
    
    readings = thermocouple.initReadings(conf.readings)
    readings, myReadings = thermocouple.read_thermocouples(readings)

    # temperature_data = ', '.join([str(value[2]) for value in readings.values()])
    temperature_data, internal_data = thermocouple.allReadings(readings)
    org_data, org_inter = thermocouple.allReadings(myReadings)
    date_time, _, _ = realtc.formattime(time.localtime())
    out = ','.join([str(sequence), date_time, temperature_data, internal_data])
    print(out)

    #-------------------------------------------
    print("Type 'exit' to stop:")
    BoardPos = input("Enter board position (1-5):")
    if 'exit' == BoardPos:
        # break
        print("THIS WOULD NORMALLY EXIT")
    TCId = input('Enter thermocouple id ("101", "T2", etc.):')
    TCId = "1"
    RefTemp = input("Enter reference temperature in celsius (0.00):")
    # convert string values into clean values and correct types
    BoardPos = BoardPos.strip()
    TCId = TCId.int()
    RefTemp = float(RefTemp)
    # only try to callibrate if the sensor entry already exists in the conf.py file
    if callibrate.verify_sensor(BoardPos, TCId, RefTemp):
        print("Hold thermocouple steady at reference and wait for confirmation or Failed message.")
        print("Callibrating...")
        callibrate.callibrate(BoardPos, TCId)
    else:
        print(f"Sensor ID {TCId} was not found.\n")


if __name__ == "__main__":
    try:
        print(f'reset code: {machine.reset_cause()}')
        main()
    except KeyboardInterrupt as e:
        print(f'Got ctrl-c {e}')
        D8.off()
        sys.exit() # TODO this falls through and resets???? okay for now
    finally: 
        print(f'Fatal error, restarting.  {machine.reset_cause()}')
        D8.off()
        machine.reset()





