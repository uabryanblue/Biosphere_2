from machine import Pin
# # the 4 digital outs to select 16 analog MUX values
# currentlly trying with just 2 pins
D0 = Pin(0, Pin.OUT)
D1 = Pin(3, Pin.OUT)
# D2 = Pin(4, Pin.OUT)

# signal
D3 = Pin(1, Pin.OUT)

def signal0():
    D0.off()
    D1.off()
    D3.on()

def signal1():
    D0.on()
    D1.off()
    D3.on()

def signal_off():
    D0.off()
    D1.off()
    D3.off()






# THIS CODE IS A BACKUP OF SOME EXPLORATION
# IT NEEDS REMOVED FOR THE FINAL VERSION

# pot = ADC(0)

# # the 4 digital outs to select 16 analog MUX values
# D0 = Pin(16, Pin.OUT)
# D1 = Pin(5, Pin.OUT)
# D2 = Pin(4, Pin.OUT)
# D3 = Pin(0, Pin.OUT)

# # # relay
# # D5 = Pin(14, Pin.OUT)
# # D6 = Pin(12, Pin.OUT)
# # D5.off()
# # D6.off()

# # analog all to value 0
# D0.off()
# D1.off()
# D2.off()
# D3.off()

# def AnalogRead():
#   val = 0
#   for i in range(0,5):
#     sleep(0.1)
#     val += pot.read()
#   return val/5

# while True:
#   val0=0
#   val1=0
#   val2=0

#   D0.off()
#   D1.off()
#   D2.off()
#   D3.off()
#   # sleep(0.5)
#   # val0 = pot.read()
#   val0 = AnalogRead()
#   # print(f"0000: {pot_value}")

#   D0.on()
#   D1.off()
#   D2.off()
#   D3.off()
#   # sleep(0.5)
#   val1 = AnalogRead()
#   # print(f"0001: {pot_value}")

#   D0.off()
#   D1.on()
#   D2.off()
#   D3.off()
#   # sleep(0.5)
#   val2 = AnalogRead()
#   # print(f"0001: {pot_value}")

#   D0.on()
#   D1.on()
#   D2.off()
#   D3.off()
#   # sleep(0.5)
#   val3 = AnalogRead()
#   # print(f"0001: {pot_value}")

#   D0.off()
#   D1.off()
#   D2.on()
#   D3.off()
#   # sleep(0.5)
#   val4 = AnalogRead()
#   # print(f"0001: {pot_value}")

#   D0.on()
#   D1.on()
#   D2.on()
#   D3.on()
#   # sleep(0.5)
#   val15 = AnalogRead()
#   # print(f"1110: {pot_valude}")


#   print(f"C0:{val0:5} | C1{val1:5} | C2{val2:5} | C3:{val3:5} | C4:{val4:5} |C15:{val15:5}")

# # # relay code
# #   D5.on()
# #   sleep(15)
# #   D5.off()
# #   sleep(1)

# #   D6.on()
# #   sleep(15)
# #   D6.off()
# #   sleep(1)

# #   D5.on()
# #   D6.on()
# #   sleep(30)
# #   D5.off()
# #   D6.off()

#   sleep(3)
