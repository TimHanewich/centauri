import sys
import time
import select
import machine
from HC12 import HC12

# define LED error sequence
led = machine.Pin("LED", machine.Pin.OUT)
led.off() # ensure LED is off while setting up.
def ERROR_SEQ() -> None:
    while True:
        led.on()
        time.sleep(1.0)
        led.off()
        time.sleep(1.0)

# define sending transceiver message to PC
def send_tran_msg(msg:str) -> None:
    """Send a transceiver-level message to the PC via USB, flagged as such. Note, this is NOT for sending the normal payload from the drone to the PC. Instead, this is ONLY for sending transceiver-level communication to the PC; messages that originate from this transceiver itself, not the drone (not passing along a message from the drone)."""
    ToSend:str = "TRAN" + msg + "\r\n" # "TRAN" means it is a message from the transceiver... not something we are passing along from the quadcopter
    sys.stdout.buffer.write(ToSend.encode())

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
    send_tran_msg("HC-12 not confirmed to be connected! Unable to establish communications.")
    ERROR_SEQ()

# Set up operating mode of HC12
time.sleep(0.5)
try:
    hc12.mode = 3 # Set to FU3 (default), general-purpose mode
except Exception as ex:
    send_tran_msg("Failure while setting HC-12 operating mode to FU3! Failing. Msg: " + str(ex))
    ERROR_SEQ()

# Configure the HC-12: channel
time.sleep(0.5)
try:
    hc12.channel = 2
except Exception as ex:
    send_tran_msg("HC-12 channel setting to 1 unsuccesful. Failing. Msg: " + str(ex))
    ERROR_SEQ()

# Configure the HC-12: Transmit power
time.sleep(0.5)
try:
    hc12.power = 8
except Exception as ex:
    send_tran_msg("HC-12 transmit power set failed! Failing. Msg: " + str(ex))
    ERROR_SEQ()

# declare buffer of receied bytes we will add to and pull from as data comes in
buffer:bytes = bytes()

# infinite respond loop
led.on() # turn on LED light
try:
    while True:
        
        # Check if we have received data from the PC that we may need to respond to or pass along to the drone (via HC-12)
        if select.select([sys.stdin], [], [], 0)[0]: # if there is data to read. That expression returns a list of data available to read. In Python, if a list is empty, it returns False. If it has something in it, it returns True
            
            # collect bytes by new line 
            data:bytes = sys.stdin.buffer.readline() # yes, it is acceptable to block here

            # If the incoming message has "TRAN" prepended to it, that means the PC is intending to talk to us, the transceiver, directly!
            # if it does NOT have "TRAN" preprended, the message it is giving it intends to be passed along to the drone via HC-12 as is
            if data.startswith("TRAN".encode()):
                data = data[4:] # strip the "TRAN" off (first four bytes)
                data = data[0:-2] # take off the "\r\n" at the end (two bytes, 13 and 10)
                if data == "PING".encode():
                    send_tran_msg("PONG")
                elif data == "STATUS?".encode(): # an inquiry of the HC-12's status
                    send_tran_msg(str(hc12.status)) # hc12.status includes the mode, channel, and power, i.e. "{'mode': 3, 'channel': 1, 'power': 8}"
                else: # it is an unknow message, so just return with a question mark so the PC knows we had no idea what it wanted
                    send_tran_msg("?")
            else: # it is intended to be directly delivered to the drone, so just pass it along via HC-12
                #hc12.send(data) # send all the data. Including the \r\n at the end!
                pass

        # check if we have received data from the HC-12 (something from the drone!) that must be passed along to the PC
        newdata:bytes = hc12.receive() # receive new data. hc12.receive returns b'' (empty bytes) if there is nothing new to be had. Note: I know it can be tempting here just to append hc12.receive() to the buffer every time, and that is what I originally had. However, this is very performanced-prohibitive and results in memory being used up after only a few thousand cycles because each time this happens, a new bytes object has to be made.
        if len(newdata) > 0:
            buffer = buffer + newdata # append any received bytes. May be more efficient to use bytearray here and "extend" what is being received
            while "\r\n".encode() in buffer: # if we have at least one full line

                # get the line
                loc:int = buffer.find("\r\n".encode())
                ThisLine:bytes = buffer[0:loc+2] # include the \r\n at the end (why we +2)
                buffer = buffer[loc+2:] # remove the line

                # send the line to the PC (including the "\r\n"!)
                sys.stdout.buffer.write(ThisLine)
        
        # wait
        time.sleep(0.01)
except Exception as ex:
    send_tran_msg("FATAL ERROR IN TRANSCEIVER: " + str(ex))
    ERROR_SEQ()