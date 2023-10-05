"""ESPNow operations for ESP8266 other microcontrollers may not work with this code"""

import time
import espnow
import network
import conf


def wifi_reset():   # Reset wifi to AP_IF off, STA_IF on and disconnected
    """wifi needs turned off so that ESPNow can take over
    call init_esp_connect() after resetting wifi """
    sta = network.WLAN(network.STA_IF)
    sta.active(False)
    ap = network.WLAN(network.AP_IF)
    ap.active(False)
    sta.active(True)
    while not sta.active():
        time.sleep(0.1)
    sta.disconnect()   # For ESP8266
    while sta.isconnected():
        time.sleep(0.1)
    return sta, ap


def init_esp_connection(sta):
    """creates and espnow object, wifi_reset() needs called before this"""
    esp = espnow.ESPNow()
    esp.active(True)

    # MAC addresses of peers
    # values are stored in conf.py
    [esp.add_peer(val) for val in conf.peers['DATA_LOGGER']]

    return esp


def get_mac(sta):
    """ get the MAC address and return it as a binary abd human readable value
    """

    binaryMac = sta.config('mac')
    # change binary to human readable:
    # humanMac = ':'.join(['{:02x}'.format(b) for b in binaryMac])

    return binaryMac


def esp_tx(peer, e, msg):

    try:
        # transmit data and check receive status
        res = e.send(conf.peers['TIME'][0], msg, True)  # only one TIME entry should exist
        if not res:
            print(f"DATA NOT RECORDED response:{res} from {peer}")

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
    host, msg = esp_con.recv(timeout)  # ms timeout on receive
    # TODO change this to trap for errors, no need to check the msg
    if msg:
        if msg == b'get_time':
            # send time to sender
            print("host: {host} requested time")
        else:
            print(f"received from: {host}, message: {msg}")

    return host, msg
