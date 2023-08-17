
import machine
import conf
import realtc
import espnowex

import calibrate

# TODO common code, should be abstracted out of main.py
def init_device():

    # turn off wifi and connect with ESPNow
    sta, ap = espnowex.wifi_reset()
    esp_con = espnowex.init_esp_connection(sta)

    # convert hex into readable mac address
    RAW_MAC = espnowex.get_mac(sta)
    MY_MAC = ":".join(["{:02x}".format(b) for b in RAW_MAC])
    print(f"My MAC addres:: {MY_MAC} raw MAC:: {RAW_MAC}")

    return esp_con, sta, RAW_MAC


def main():
    print("--------START DEVICE--------")
    
    # on board relay control, put in the off state
    D8 = machine.Pin(15, machine.Pin.OUT)
    D8.off() # turn pin low

    esp_con, station, RAW_MAC = init_device()

    # verify that the conf.py file is associated with this code base
    print("\n================ MY CONFIGURATION ================")
    print("MY DATA LOGGERS")
    [print(val) for val in conf.peers['DATA_LOGGER']]
    print("MY TIME SERVER")
    [print(val) for val in conf.peers['TIME']]
    print("==================================================\n")
    realtc.get_remote_time(esp_con)

    print('\nNOTE: Although readings are sent wirelessly to a data logger, there is no confirmation they are actually recorded.')
    print('You should verify data is recorded after the first stored value by looking at the data logger storage.')
    print('Future versions will include a confirmation message that the data was recorded.\n')

    calibrate.calibrate_main(esp_con, station, RAW_MAC)



if __name__ == "__main__":
    try:
        print(f"reset code: {machine.reset_cause()}")
        main()
    except KeyboardInterrupt as e:
        print(f"Got ctrl-c {e}")
        