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

# declare buffer of receied bytes
rxBuffer_fromPC:bytearray = bytearray()       # buffer of all bytes received from PC
rxBuffer_fromHC12:bytearray = bytearray()     # butfer for bytes received from quadcopter via HC-12

# infinite respond loop
led.on() # turn on LED light
try:
    while True:

        # continuously collect data, byte by byte while there is data still available
        while select.select([sys.stdin], [], [], 0)[0]: # if there is data to read. That expression returns "[sys.stdin]" if there is data to read and "[]" if not. In Python, if a list is empty, it returns False. If it has something in it, it returns True
            print("There is data to read!")
            NewBytes:bytes = sys.stdin.buffer.read(1)
            print("Read this: " + str(NewBytes))
            rxBuffer_fromPC.extend(NewBytes) # read one byte and append it to the buffer

        # if we have any new lines worth working on (separator/terminator), handle those now
        while "\r\n".encode() in rxBuffer_fromPC:

            # get the line
            loc:int = rxBuffer_fromPC.find("\r\n".encode())
            ThisLine:bytes = rxBuffer_fromPC[0:loc+2] # include the \r\n at the end (why we +2)
            rxBuffer_fromPC = rxBuffer_fromPC[loc+2:] # remove the line

            # Handle the line
            if ThisLine.startswith("TRAN".encode()):
                if ThisLine == "TRANPING\r\n".encode():
                    send_tran_msg("PONG")
                elif ThisLine == "TRANSTATUS?\r\n".encode():
                    send_tran_msg(str(hc12.status)) # hc12.status includes the mode, channel, and power, i.e. "{'mode': 3, 'channel': 1, 'power': 8}"
                else: # unknown TRAN message
                    send_tran_msg("?")
            else: # it is not a TRAN message, so pass it along to the HC-12 to send it to the quadcopter
                #hc12.send(ThisLine) # send all the data. Including the \r\n at the end!
                pass

        # check if we have received data from the HC-12 (something from the drone!) that must be passed along to the PC
        newdata:bytes = hc12.receive() # receive new data. hc12.receive returns b'' (empty bytes) if there is nothing new to be had. Note: I know it can be tempting here just to append hc12.receive() to the buffer every time, and that is what I originally had. However, this is very performanced-prohibitive and results in memory being used up after only a few thousand cycles because each time this happens, a new bytes object has to be made.
        if len(newdata) > 0:
            rxBuffer_fromHC12.extend(newdata) # append any received bytes. May be more efficient to use bytearray here and "extend" what is being received
            while "\r\n".encode() in rxBuffer_fromHC12: # if we have at least one full line

                # get the line
                loc:int = rxBuffer_fromHC12.find("\r\n".encode())
                ThisLine:bytes = rxBuffer_fromHC12[0:loc+2] # include the \r\n at the end (why we +2)
                rxBuffer_fromHC12 = rxBuffer_fromHC12[loc+2:] # remove the line

                # send the line to the PC (including the "\r\n"!)
                sys.stdout.buffer.write(ThisLine)
        
        # wait
        time.sleep(0.01)
except Exception as ex:

    msg:str = "FATAL ERROR IN TRANSCEIVER: " + str(ex)

    # send to PC
    send_tran_msg(msg)

    # save the error to a file
    f = open("errors.txt", "a")
    f.write(msg + "\n\n")
    f.close()

    ERROR_SEQ()