import sys
import time
import select

while True:
    
    # Check if there is data to be received
    if select.select([sys.stdin], [], [], 0)[0]: # if there is data to read. That expression returns a list of data available to read. In Python, if a list is empty, it returns False. If it has something in it, it returns True
        
        # collect all bytes, separarated by line
        read:bytes = bytes()
        while not read.endswith("\r\n".encode()): # read until new line
            read = read + sys.stdin.buffer.read(1) # read 1 byte. yes, it is ok to block on this as the \r\n should be coming in a moment...
        
        # Send back confirmation of what we received
        ToSend:str = "Just received this data: " + str(read) + "\r\n"
        sys.stdout.buffer.write(ToSend.encode())
    else: 
        ToSend:str = "Nothing received.\r\n"
        sys.stdout.buffer.write(ToSend.encode())

    # send something
    ToSend:str = str(time.ticks_ms()) + "\r\n"
    sys.stdout.buffer.write(ToSend.encode())

    # wait
    time.sleep(0.25)