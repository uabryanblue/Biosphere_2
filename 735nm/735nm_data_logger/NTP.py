""" portions of the code come from www.engineersgarage.com """
import machine
import network
import ntptime
# import realtc
import time
import ds3231_gen
import sys
import gc

print(f"START") # use to get clean output after garbage in console

station = network.WLAN(network.STA_IF)

def connect(id, pswd):
  ssid = id
  password = pswd
  print(f"Trying to connect to SSID: {ssid}")
  if station.isconnected() == True:
    print("Already connected")
    return
  station.active(True)
  station.connect(ssid, password)
  counter = 0
  while (station.isconnected() == False) and (counter < 1000):
    counter += 1
    time.sleep_ms(10)
    pass
  if counter >= 1000:
    print(f"FAILD ON NTP")
    sys.exit()
  print("Connection successful")
  print(station.ifconfig())
 
def disconnect():
  if station.active() == True: 
   station.active(False)
  if station.isconnected() == False:
    print("Disconnected") 
 
def set_ds3231(rtc, ds3231):
  """set the time for the RTC DS3231 board"""

  # rtc.datetime((YY, MM, DD, wday, hh, mm, ss, 0))
  (year, month, day, weekday, hours, minutes, seconds, subseconds) = rtc.datetime()
  # YY, MM, DD, hh, mm, ss, wday, _ = ds3231.get_time()
  ds3231.set_time((year, month, day, hours, minutes, seconds, weekday, subseconds))
  # rtc.datetime((YY, MM, DD, wday, hh, mm, ss, 0))
  gc.collect()

def formatrtc(in_time):
    """RTC format time produce a date/time format from tuple
    only minute resolution supported"""
    # rtc.datetime((YY, MM, DD, wday, hh, mm, ss, 0))

    # YYYY-MM-DD hh:mm:ss
    date = f'{in_time[0]}-{in_time[1]:0>2}-{in_time[2]:0>2}'
    time = f'{in_time[4]:0>2}:{in_time[5]:0>2}:{in_time[6]:0>2}'
    formatted_time = date + ' ' + time
    
    return formatted_time


def main():

  connect("Lazuline", "visk972/")

  rtc = machine.RTC()

  i2c = machine.I2C(sda=machine.Pin(4), scl=machine.Pin(5))
  ds3231 = ds3231_gen.DS3231(i2c)

  ntptime.settime()

  (year, month, day, weekday, hours, minutes, seconds, subseconds) = rtc.datetime()
  print ("UTC Time: ")
  print((year, month, day, hours, minutes, seconds))

  sec = ntptime.time()
  timezone_hour = -7 # arizona -7 tz
  timezone_sec = timezone_hour * 3600
  sec = int(sec + timezone_sec)
  (year, month, day, hours, minutes, seconds, weekday, yearday) = time.localtime(sec)

  # print ("IST Time: ")

  print(f"IST Time (arizona -7 tz): {(year, month, day, hours, minutes, seconds, weekday, yearday)}")
  rtc.datetime((year, month, day, weekday, hours, minutes, seconds, 0))
  # print(f"rtc after being set: {rtc.datetime()}")

  # set the external battery backed up ds3231
  YY, MM, DD, wday, HH, mm, s, ss = rtc.datetime()
  # YY, MM, DD, hh, mm, ss, wday, _ = ds3231.get_time()
  ds3231.set_time((YY, MM, DD, HH, mm, s, wday, ss))
  # print(f"sd3231 after set raw: {(YY, MM, DD, HH, mm, s, wday, ss)}")
  disconnect()

  print(f"\nDS3231 get_time:   {ds3231.get_time()}")
  print(f"rtc datetime:      {rtc.datetime()}")
  print(f'time localtime:    {time.localtime()}')
  # print(f"DS3231, rtc, time:     {ds3231.get_time()}  {rtc.datetime()}  {time.localtime()}  ")

  print(f"\n**** TIME HAS BEEN SET TO: {formatrtc(rtc.datetime())} ****")

if __name__ == "__main__":
    try:
        print(f"reset code: {machine.reset_cause()}")
        main()
    except KeyboardInterrupt as e:
        print(f"Got   ctrl-c {e}")
    finally:
        print(f"Fatal error")
