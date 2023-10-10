""" portions of the code come from www.engineersgarage.com """
import machine
import network
import ntptime
import time
import ds3231_gen
import gc

station = network.WLAN(network.STA_IF)

def connect(id, pswd):
  ssid = id
  password = pswd
  if station.isconnected() == True:
    print("Already connected")
    return
  station.active(True)
  station.connect(ssid, password)
  while station.isconnected() == False:
    pass
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

connect("Lazuline", "visk972/")

rtc = machine.RTC()

i2c = machine.I2C(sda=machine.Pin(4), scl=machine.Pin(5))
ds3231 = ds3231_gen.DS3231(i2c)

ntptime.settime()

#######################


# def set_time():
#     ntptime.settime()
#     tm = utime.localtime()
#     tm = tm[0:3] + (0,) + tm[3:6] + (0,)
#     machine.RTC().datetime(tm)
#     print('current time: {}'.format(utime.localtime())) 

######################

(year, month, day, weekday, hours, minutes, seconds, subseconds) = rtc.datetime()
print ("UTC Time: ")
print((year, month, day, hours, minutes, seconds))

sec = ntptime.time()
timezone_hour = -7 # arizona -7 tz
timezone_sec = timezone_hour * 3600
sec = int(sec + timezone_sec)
(year, month, day, hours, minutes, seconds, weekday, yearday) = time.localtime(sec)

# print ("IST Time: ")

print(f"IST Time: {(year, month, day, hours, minutes, seconds, weekday, yearday)}")
rtc.datetime((year, month, day, weekday, hours, minutes, seconds, 0))
print(f"rtc after being set: {rtc.datetime()}")

# set the external battery backed up ds3231
YY, MM, DD, wday, HH, mm, s, ss = rtc.datetime()
# YY, MM, DD, hh, mm, ss, wday, _ = ds3231.get_time()
ds3231.set_time((YY, MM, DD, HH, mm, s, wday, ss))
print(f"sd3231 after set raw: {(YY, MM, DD, HH, mm, s, wday, ss)}")
disconnect()

print(f"DS3231 time:     {ds3231.get_time()}")
print(f"rtc local time:  {rtc.datetime()}")
print(f'time local time: {time.localtime()}')

print(f"DS3231, rtc, time:     {ds3231.get_time()}  {rtc.datetime()}  {time.localtime()}  ")
