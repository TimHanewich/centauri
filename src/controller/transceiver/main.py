import sys
import time
import select

while True:
    
    # Check if we have received data from the PC
    if select.select([sys.stdin], [], [], 0)[0]: # if there is data to read. That expression returns a list of data available to read. In Python, if a list is empty, it returns False. If it has something in it, it returns True
        
        # collect all bytes, separarated by line
        data:bytes = bytes()
        while not data.endswith("\r\n".encode()): # read until new line
            data = data + sys.stdin.buffer.read(1) # read 1 byte. yes, it is ok to block on this as the \r\n should be coming in a moment...
        
        # take off the "\r\n" at the end (two bytes, 13 and 10)
        data = data[0:-2]

        # if it starts with "SEND" encoded as bytes, we know the PC intends only for us to pass this along to the HC-12 to be sent, so do that.
        # otherwise, it is a message for US, not the the HC-12!
        if data.startswith("SEND".encode()): # 83, 69, 78, 68 in bytes = "SEND". Meaning the PC wants us to just pass it along to the HC-12 to be sent to the drone
            data = data[4:] # strip the "SEND" off (first four bytes)
            # send it to HC-12 now
        else: # it did not start with SEND, so it is a message from the PC for us!
            if data == "PING".encode():
                ToSend:str = "TRAN" + "PONG" + "\r\n" # "TRAN" means it is a message from the transceiver... not something we are passing along from the quadcopter
                sys.stdout.buffer.write(ToSend.encode())
            else: # unknow message
                ToSend:str = "TRAN" + "?" + "\r\n"
                sys.stdout.buffer.write(ToSend.encode())


    # check if we have received data from the HC-12 (something from the drone!)
    # check here


    # wait
    time.sleep(0.01)