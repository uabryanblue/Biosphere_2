
import machine
import conf
import realtc
import espnowex

# THESE ARE IMPORTED AS NEEDED TO SAVE SPACE
# CHECK THE BLOCK OF ROLES
# import calibrate
# import datalogger_main
# import BME280_main
# import TRC_main  


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
    print("--------START DEVICE--------")
    esp_con, station, RAW_MAC = init_device()
    # only get the remote time if you are the time source
    # TODO change to the TIME entry in conf as a comparison
    # if conf.MYROLE != "DATALOGGER":
    print(f"time set and my role is {conf.MYROLE}")
    
    # # use the conf.py file to select the roll of the device
    # # and then call the appropriate startup
    # if conf.MYROLE == "CALIBRATE":
    #     print("Calibration Mode (terminal window)")
    #     import calibrate
    #     calibrate.calibrate_main()
    # elif conf.MYROLE == "DATALOGGER":
    if conf.MYROLE == "DATALOGGER":
        print("Data Logger")
        import datalogger_main
        datalogger_main.data_looger_main(esp_con, station, RAW_MAC)
    # elif conf.MYROLE == "TRCCONTROL":
    #     # realtc.get_remote_time(esp_con)
    #     print("Temperature Relay Controller")
    #     import TRC_main
    #     TRC_main.trc_main(esp_con, station)
    #     # call the thermocouple and relay control main here
    # elif conf.MYROLE == "THP":
    #     # realtc.get_remote_time(esp_con)
    #     # call the temp/humidity/pressure main here
    #     print("BME280 Temp/Humidity/Pressure")
    #     # BME280_main.main()


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
