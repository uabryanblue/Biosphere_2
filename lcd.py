# from machine import Pin, I2C
import machine
from ssd1306 import SSD1306_I2C
from time import sleep

# display found at address:  0x3c


def scanI2C():
    # sdaPIN=machine.Pin(4)  #for ESP32
    # sclPIN=machine.Pin(5)

    # i2c=machine.I2C(sda=sdaPIN, scl=sclPIN, freq=10000)
    i2c = machine.I2C(sda=machine.Pin(4), scl=machine.Pin(5))
    devices = i2c.scan()
    if len(devices) == 0:
        print("No i2c device !")
    else:
        print("i2c devices found:", len(devices))
    for device in devices:
        print("At address: ", hex(device))


def testLCD():
    # I2C_ADDR = 0x3c

    totalRows = 32
    totalColumns = 128

    i2c = machine.I2C(sda=machine.Pin(4), scl=machine.Pin(5))
    print("created i2c led")
    oled = SSD1306_I2C(128, 64, i2c)
    print("oled setup")
    # oled.fill(1)
    # oled.show()
    # oled.fill(0)
    # oled.show()

    oled.poweron()
    oled.text("Hello", 0, 0)
    oled.text("World", 0, 10)
    oled.show()

    print("oled done")
    # print("init i2c for lcd")
    # oled_width = 128
    # oled_height = 64

    # oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)
    # print("init oled")

    # oled.text('Welcome', 0, 0)
    # oled.text('OLED Display', 0, 10)
    # oled.text('how2electronics', 0, 20)
    # oled.text('Makerfabs', 0, 30)

    # oled.show()
