import sys
import time
import select

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