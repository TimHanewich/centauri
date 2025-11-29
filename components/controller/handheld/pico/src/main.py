import time
import machine

uart = machine.UART(0, baudrate=9600, tx=machine.Pin(16), rx=machine.Pin(17))

rxBuffer:bytearray = bytearray()

while True:
    
    # receive?
    ba:int = uart.any()
    if ba > 0:
        data = uart.read(ba)
        rxBuffer.extend(data)
    
    # Do we have a line?
    term_loc:int = rxBuffer.find("\r\n".encode())
    if term_loc != -1:
        ThisLine:bytes = rxBuffer[0:term_loc+2]
        rxBuffer = rxBuffer[16:] # keep the rest, trim out that line
        print(ThisLine)
        
    time.sleep(0.01)
