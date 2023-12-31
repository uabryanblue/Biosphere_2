

import espnow
import network
import time

import network, time

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

    # MAC address of peer's wifi interface
    # example: b'\x5c\xcf\x7f\xf0\x06\xda'
    # TODO peers should be in the conf file
    # peer = b'\x8c\xaa\xb5M\x7f\x18'  # my #2 esp8266
    # peer = b'\xec\xfa\xbc\xcb\xab\xce' # 1st datalogger
    peer1 = b'\xc4[\xbe\xe4\xfdq'
    peer2 = b'\x8c\xaa\xb5M\x7f\x18'
    e.add_peer(peer1) # register the peer for espnow communication
    e.add_peer(peer2) # register the peer for espnow communication

    return e


def get_mac(wlan_sta):
    """ get the MAC address and return it as a binary value
    change binary to human readable:
    ':'.join(['{:02x}'.format(b) for b in espnowex.get_mac()])
    """

    # TODO add some error handling
    wlan_mac = wlan_sta.config('mac')
    
    return wlan_mac


def esp_tx(peer, e, msg):

    # TODO add support for TX to multiple peers
    # # MAC address of peer1's wifi interface exmaple:
    # # peer1 = b'\xe8\x68\xe7\x4e\xbb\x19'
    # the receiver MAC address
    # peer = b'\x8c\xaa\xb5M\x7f\x18'  # my #2 esp8266
    # peer = b'\xec\xfa\xbc\xcb\xab\xce' # 1st datalogger
    
    # peer = b'\xc4[\xbe\xe4\xfdq'

    try:
        res = e.send(peer, msg, True)  # transmit data and check receive status
        if not res:
            print(f"DATA NOT RECORDED response:{res}")
        else:
            print(f"DATA TX SUCCESSFUL response:{res}")

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
        if msg == b'get_time':
            # send time to sender
            print("host: {host} requested time")
        else:
            print(f"received from: {host}, message: {msg}")
    
    return host, msg
                