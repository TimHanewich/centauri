import sys
import time
import select
import machine
from HC12 import HC12

# define LED error sequence
led = machine.Pin("LED", machine.Pin.OUT)
def ERROR_SEQ() -> None:
    while True:
        led.on()
        time.sleep(1.0)
        led.off()
        time.sleep(1.0)

# set up HC-12
uart = machine.UART(0, rx=machine.Pin(17), tx=machine.Pin(16), baudrate=9600)
set_pin:int = 22
hc12 = HC12(uart, set_pin)

# pulse HC-12
pulsed:bool = False
for _ in range(5): # attempts
    if not pulsed:
        time.sleep(0.25)
        pulsed = hc12.pulse
if not pulsed:
    print("HC-12 not confirmed to be connected! Unable to establish communications.")
    ERROR_SEQ()

# infinite respond loop
led.on() # turn on LED light
while True:
    
    # Check if we have received data from the PC that we may need to respond to or pass along to the drone (via HC-12)
    if select.select([sys.stdin], [], [], 0)[0]: # if there is data to read. That expression returns a list of data available to read. In Python, if a list is empty, it returns False. If it has something in it, it returns True
        
        # collect all bytes, separarated by line
        data:bytes = bytes()
        while not data.endswith("\r\n".encode()): # read until new line
            data = data + sys.stdin.buffer.read(1) # read 1 byte. yes, it is ok to block on this as the \r\n should be coming in a moment...

        # If the incoming message has "TRAN" prepended to it, that means the PC is intending to talk to us, the transceiver, directly!
        # if it does NOT have "TRAN" preprended, the message it is giving it intends to be passed along to the drone via HC-12 as is
        if data.startswith("TRAN".encode()):
            data = data[4:] # strip the "TRAN" off (first four bytes)
            data = data[0:-2] # take off the "\r\n" at the end (two bytes, 13 and 10)
            if data == "PING".encode():
                ToSend:str = "TRAN" + "PONG" + "\r\n" # "TRAN" means it is a message from the transceiver... not something we are passing along from the quadcopter
                sys.stdout.buffer.write(ToSend.encode())
            else: # unknow message
                ToSend:str = "TRAN" + "?" + "\r\n"
                sys.stdout.buffer.write(ToSend.encode())
        else: # it is intended to be directly delivered to the drone, so just pass it along via HC-12
            # send it to HC-12 now
            pass


    # check if we have received data from the HC-12 (something from the drone!) that must be passed along to the PC
    # check here

    # wait
    time.sleep(0.01)