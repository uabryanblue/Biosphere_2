"""ESPNow operations for ESP8266 other microcontrollers may not work with this code"""

import time
import espnow
import network
import conf


def wifi_reset():   # Reset wifi to AP_IF off, STA_IF on and disconnected
    sta = network.WLAN(network.STA_IF); sta.active(False)
    ap = network.WLAN(network.AP_IF); ap.active(False)
    sta.active(True)
    while not sta.active():
        time.sleep(0.1)
    sta.disconnect()   # For ESP8266
    while sta.isconnected():
        time.sleep(0.1)
    return sta, ap


def init_esp_connection(sta):
    """creates and espnow object, wifi_reset() needs called before this"""
    # create espnow connection
    e = espnow.ESPNow()
    e.active(True)

    # MAC address of others that data needs sent to
    # example: b'\x5c\xcf\x7f\xf0\x06\xda'
    [e.add_peer(val) for val in conf.peers['DATA_LOGGER']]
    return e


def get_mac(wlan_sta):
    """ get the MAC address and return it as a binary value
    """

    # TODO add some error handling
    wlan_mac = wlan_sta.config('mac')
    
    return wlan_mac


def esp_tx(peer, esp_con, msg):
    try:
        # response checking does on work on ESP8266
        res = esp_con.send(peer, msg, True) 
        print(f"sent to {peer}")
        print(f"{msg}")
 
    except OSError as err:
        if err.args[0] == errno.ETIMEDOUT:  # standard timeout is okay, ignore it
            print("ETIMEDOUT found")  # timeout is okay, ignore it
        else:  # general case, close the socket and continue processing, prevent hanging
            print(f"ERROR: {err}")

    return res


def esp_rx(esp_con, timeout=1000):
    """init of esp connection needs performed first
    peers need to be added to the espnow connection"""

    # wait for a message to process
    host, msg = esp_con.recv(timeout) # ms timeout on receive
    # TODO change this to trap for errors, no need to check the msg
    if msg:
        if msg == b'GET_TIME':
            # send time to sender
            print("host: {host} requested time")
        else:
            print(f"received from: {host}, message: {msg}")
    
    return host, msg
