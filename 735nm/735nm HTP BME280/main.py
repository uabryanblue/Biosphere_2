
import machine
import conf
import realtc
import espnowex
import BME280_main
import gc

def init_device():

    # turn off wifi and connect with ESPNow
    sta, ap = espnowex.wifi_reset()
    esp_con = espnowex.init_esp_connection(sta)

    # convert hex into readable mac address
    RAW_MAC, MY_MAC = espnowex.get_mac(sta)
    # MY_MAC = ":".join(["{:02x}".format(b) for b in RAW_MAC])
    print(f"My MAC addres:: {MY_MAC} raw MAC:: {RAW_MAC}")

    return esp_con, sta, RAW_MAC


def main():
    gc.collect()
    print("--------START DEVICE--------")
    esp_con, station, RAW_MAC = init_device()
    gc.collect()
    # only get the remote time if you are the time source
    print(f"time set and my role is {conf.MYROLE}")
    
    if conf.MYROLE == "THP":
        print("THP BME280")
        # datalogger_main.data_looger_main(esp_con, station, RAW_MAC)
    else:
        print("THIS CONFIGURATION FILE IS NOT FOR A TMP BME280!")

    # start the main THP data collection
    BME280_main.thp_main(esp_con, RAW_MAC)

    # BME280_main.main(esp_con, RAW_MAC)

if __name__ == "__main__":
    try:
        print(f"reset code: {machine.reset_cause()}")
        main()
    except KeyboardInterrupt as e:
        print(f"Got ctrl-c {e}")
        # D8.off() # TODO D8 HAS TO BE SET TO OFF ON ERROR !!!!!!!!!!!!!!!!!!
        # sys.exit()  # TODO this falls through and resets???? okay for now
    finally:
        print(f"Fatal error, restarting.  {machine.reset_cause()}")
        # D8.off() # TODO D8 HAS TO BE SET TO OFF ON ERROR !!!!!!!!!!!!!!!!!!
        machine.reset()
