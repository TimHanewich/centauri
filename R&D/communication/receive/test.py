import machine
import time
import gc

# set up UART interface for radio communications via HC-12
print("Setting up HC-12 via UART...")
hc12_set = machine.Pin(20, machine.Pin.OUT) # the SET pin, used for going into and out of AT mode
uart_hc12 = machine.UART(0, tx=machine.Pin(16), rx=machine.Pin(17), baudrate=9600)
uart_hc12.read(uart_hc12.any()) # clear out any RX buffer that may exist

# pulse HC-12
hc12_set.low() # pull it LOW to enter AT command mode
time.sleep(0.2) # wait a moment for AT mode to be entered
hc12_pulsed:bool = False
hc12_pulse_attempts:int = 0
hc12_pulse_rx_buffer:bytearray = bytearray()
while hc12_pulsed == False and hc12_pulse_attempts < 3:
    print("Sending pulse attempt # " + str(hc12_pulse_attempts + 1) + "...")
    uart_hc12.write("AT\r\n".encode()) # send AT command
    hc12_pulse_attempts = hc12_pulse_attempts + 1
    time.sleep(0.2) # wait a moment for it to be responded to

    # if there is data
    if uart_hc12.any():
        hc12_pulse_rx_buffer.extend(uart_hc12.read(uart_hc12.any())) # append
        if "OK\r\n".encode() in hc12_pulse_rx_buffer:
            hc12_pulsed = True
            print("Pulse received!")
            break
        else:
            print("Data received back from HC-12 but it wasn't an OK (pulse)")
    else:
        print("No data received from HC-12.")

    # wait
    time.sleep(1.0)

# Configure HC-12 while still in AT mode: mode = FU3
print("Setting HC-12 mode to FU3...")
uart_hc12.write("AT+FU3\r\n".encode()) # go into mode FU3 (normal mode)
time.sleep(0.2) # wait a moment
response:bytes = uart_hc12.read(uart_hc12.any())
if "OK+FU3\r\n".encode() in response:
    print("HC-12 in FU3 mode successful!")
else:
    print("HC-12 not confirmed to be in HC-12 mode!")
    exit()

# Configure HC-12 while still in AT mode: channel = 2
print("Setting HC-12 channel to 2...")
uart_hc12.write("AT+C002\r\n".encode())
time.sleep(0.2) # wait a moment
response:bytes = uart_hc12.read(uart_hc12.any())
if "OK+C002\r\n".encode() in response:
    print("HC-12 set to channel 2!")
else:
    print("HC-12 not confirmed to be in channel 2.")
    exit()

# Configure HC-12 while still in AT mode: power
print("Setting HC-12 power to maximum level of 8...")
uart_hc12.write("AT+P8\r\n".encode())
time.sleep(0.2) # wait a moment
response:bytes = uart_hc12.read(uart_hc12.any())
if "OK+P8\r\n".encode() in response:
    print("HC-12 power set to level 8 (20 dBM)")
else:
    print("Unsuccessful in setting HC-12 power level to 8.")
    exit()

# now that the HC-12 is set up and configured, close out of AT mode by setting the SET pin back to HIGH
print("Returning HC-12 SET pin to HIGH (exiting AT mode)...")
hc12_set.high()
time.sleep(0.5) # wait a moment for the HC-12 to successfully get out of AT mode before proceeding with sending any messages


# Setup
rxBuffer:bytearray = bytearray(3)      # 128 = maximum length of single receive
ToProcess:bytearray = bytearray(256)     

# read
while True:

    # read
    bytesavailable:int = uart_hc12.any()
    if bytesavailable > 0:
        mem1 = gc.mem_free()
        bytesread:int = uart_hc12.readinto(rxBuffer, bytesavailable)
        for i in range(bytesread):
            ToProcess[i] = rxBuffer[i]
        mem2 = gc.mem_free()
        print("Mem usd: " + str(mem1 - mem2))

    # wait
    time.sleep(0.005)