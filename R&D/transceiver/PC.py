import serial
import time
import random

ser = serial.Serial(port="COM3", baudrate=9600, timeout=5)

last_send = time.time()

while True:

    # read
    if ser.in_waiting > 0: # more than 0 bytes waiting!
        data = ser.read(ser.in_waiting)
        print("Received data: " + str(data))

    # write?
    if (time.time() - last_send) >= 10.0:
        ToSend:str = "Here is a random number: " + str(random.randint(0, 100)) + "\r\n"
        ser.write(ToSend.encode())
        last_send = time.time()

    time.sleep(0.05)