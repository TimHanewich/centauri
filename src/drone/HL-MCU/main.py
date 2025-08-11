print("Hello! I am the Centauri quadcopter's High-Level MCU.")

# First thing is first: set up onboard LED, turn it on while loading
import machine
led = machine.Pin("LED", machine.Pin.OUT)
led.on()

# establish failure pattern
import time
def FATAL_ERROR() -> None:
    while True:
        led.on()
        time.sleep(1.0)
        led.off()
        time.sleep(1.0)

# next, set up radio communication via HC-12. 
# this is a priority to confirm it is online
from HC12 import HC12
uart_hc12:machine.UART = machine.UART(1, tx=machine.Pin(4), rx=machine.Pin(5), baudrate=9600) # 9600 baudrate is the default baudrate for the HC12
hc12:HC12 = HC12(uart_hc12, 3) # set pin = GP3
hc12_connected:bool = False
for t in range(0, 5): # 5 attempts:
    print("Attempt # " + str(t + 1) + " to validate HC-12 is connected...")
    if hc12.pulse:
        print("HC-12 connection confirmed!")
        hc12_connected = True
        break
    else:
        print("Attempt to pulse HC-12 failed.")
        time.sleep(0.5)

# if the HC-12 is not connected, fail
if hc12_connected == False:
    print("Unable to confirm HC-12 connection. Failing.")
    FATAL_ERROR()

# send out an HC-12 message to confirm we are online
import tools
print("Sending online message...")
#hc12.send(tools.pack_special_packet("online") + "\r\n".encode())
print("Online message sent.")

# confirm TF Luna is connected
from TFLuna import TFLuna
i2c_luna = machine.I2C(1, sda=machine.Pin(6), scl=machine.Pin(7))
print("IC2 Luna bus scan: " + str(i2c_luna.scan()))
luna:TFLuna = TFLuna(i2c_luna)
if luna.signature:
    print("TF Luna connected!")
    #hc12.send(tools.pack_special_packet("TF-Luna good") + "\r\n".encode())
else:
    print("TF-Luna not connected! Signature unsuccessful.")
    FATAL_ERROR()

# confirm if BMP180 is connected
from bmp085 import BMP180
i2c_bmp180 = machine.I2C(1, sda=machine.Pin(10), scl=machine.Pin(11))
print("I2C BMP180 bus scan: " + str(i2c_bmp180.scan()))
if 0x77 in i2c_bmp180.scan():
    print("BMP180 confirmed to be connected.")
    #hc12.send(tools.pack_special_packet("BMP180 good") + "\r\n".encode())
else:
    print("BMP180 not found on expected I2C bus!")
    FATAL_ERROR()
bmp180 = BMP180(i2c_bmp180)

# confirm if QMC5883L is connected
from QMC5883L import QMC5883L
i2c_qmc = machine.I2C(1, sda=machine.Pin(14), scl=machine.Pin(15))
print("I2C QMC5883L bus scan: " + str(i2c_qmc.scan()))
if 0x0D in i2c_qmc.scan():
    print("QMC5883L confirmed to be connected!")
    #hc12.send(tools.pack_special_packet("QMC5883L good") + "\r\n".encode())
else:
    print("QMC5883L not connected!")
    FATAL_ERROR()
qmc = QMC5883L(i2c_qmc)


