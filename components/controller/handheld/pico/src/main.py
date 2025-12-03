import time
import machine
import ssd1306
import tools
from display import Display




#################################
###### SET UP SSD1306 OLED! #####
#################################

# Set up the SSD1306 OLED
i2c = machine.I2C(1, sda=machine.Pin(14), scl=machine.Pin(15))
if 60 not in i2c.scan():
    print("SSD1306 not detected! Exiting.")
    exit()
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# declare display
dc:Display = Display(oled)

# display the centauri graphic during loading
print("Displaying logo...")
dc.page = "logo"
dc.display()
time.sleep(2.0) # wait for 2 seconds

# Declae fatal error function
def FATAL_ERROR() -> None:
    oled.fill(0)
    oled.text("FATAL ERROR!", 0, 0)
    oled.show()

def boot_update(status:str) -> None:
    dc.page = "boot"
    dc.boot_status = status
    dc.display()






###############################################
###### SET UP UART FOR HC-12 RADIO COMMS! #####
###############################################


# set up UART interface for radio communications via HC-12
print("Setting up HC-12 via uart_ci...")
boot_update("HC-12")
hc12_set = machine.Pin(6, machine.Pin.OUT) # the SET pin, used for going into and out of AT mode
uart_hc12 = machine.UART(1, tx=machine.Pin(4), rx=machine.Pin(5), baudrate=9600)
uart_hc12.read(uart_hc12.any()) # clear out any RX buffer that may exist

# pulse HC-12
boot_update("HC-12 Pulse")
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

# handle results of HC-12 pulse attempt
if hc12_pulsed:
    print("HC-12 pulsed! It is connected and working properly.")
else:
    print("HC-12 did not pulse back! Ensure it is connected, in baudrate 9600 mode, and working properly.")
    FATAL_ERROR()

# Configure HC-12 while still in AT mode: mode = FU3
boot_update("HC-12 Mode")
print("Setting HC-12 mode to FU3...")
uart_hc12.write("AT+FU3\r\n".encode()) # go into mode FU3 (normal mode)
time.sleep(0.2) # wait a moment
response:bytes = uart_hc12.read(uart_hc12.any())
if "OK+FU3\r\n".encode() in response:
    print("HC-12 in FU3 mode successful!")
else:
    print("HC-12 not confirmed to be in HC-12 mode!")
    FATAL_ERROR()

# Configure HC-12 while still in AT mode: channel = 2
boot_update("HC-12 Channel")
print("Setting HC-12 channel to 2...")
uart_hc12.write("AT+C002\r\n".encode())
time.sleep(0.2) # wait a moment
response:bytes = uart_hc12.read(uart_hc12.any())
if "OK+C002\r\n".encode() in response:
    print("HC-12 set to channel 2!")
else:
    print("HC-12 not confirmed to be in channel 2.")
    FATAL_ERROR()

# Configure HC-12 while still in AT mode: power
boot_update("HC-12 Power")
print("Setting HC-12 power to maximum level of 8...")
uart_hc12.write("AT+P8\r\n".encode())
time.sleep(0.2) # wait a moment
response:bytes = uart_hc12.read(uart_hc12.any())
if "OK+P8\r\n".encode() in response:
    print("HC-12 power set to level 8 (20 dBM)")
else:
    print("Unsuccessful in setting HC-12 power level to 8.")
    FATAL_ERROR()

# now that the HC-12 is set up and configured, close out of AT mode by setting the SET pin back to HIGH
boot_update("HC-12 Ready")
print("Returning HC-12 SET pin to HIGH (exiting AT mode)...")
hc12_set.high()
time.sleep(0.5) # wait a moment for the HC-12 to successfully get out of AT mode before proceeding with sending any messages









#################################################################
###### NOW SET UP UART TO RECEIVE CONTRLLER INPUT FROM RPI! #####
#################################################################

# Set up UART to receive controller input data from the RPi
boot_update("Control Input")
print("Setting up uart_ci...")
uart_ci = machine.UART(0, baudrate=9600, tx=machine.Pin(16), rx=machine.Pin(17))
print("Clearing out uart_ci...")
if uart_ci.any(): # clear out the rxbuffer
    uart_ci.read(uart_ci.any())
rxBuffer:bytearray = bytearray()

# Set up variables to contain the most up to date controller input data
# "ci" short for "controller input"
ci_last_received_ticks_us:int = None     # The last time control input was received via UART
ci_ls:bool = False                       # left stick clicked in
ci_rs:bool = False                       # right stick clicked in
ci_back:bool = False                     # back button currently pressed
ci_start:bool = False                    # start button currently pressed
ci_a:bool = False                        # a button currently pressed
ci_b:bool = False                        # b button currently pressed
ci_x:bool = False                        # x button currently pressed
ci_y:bool = False                        # y button currently pressed
ci_up:bool = False                       # D-Pad up currently pressed
ci_right:bool = False                    # D-Pad right currently pressed
ci_down:bool = False                     # D-Pad down currently pressed
ci_left:bool = False                     # D-Pad left currently pressed
ci_lb:bool = False                       # Left bumper currently pressed
ci_rb:bool = False                       # right bumper currently pressed
ci_left_x:float = 0.0                    # Left Stick X axis (left/right) = -1.0 to 1.0
ci_left_y:float = 0.0                    # Left Stick Y axis (left/right) = -1.0 to 1.0
ci_right_x:float = 0.0                   # Right Stick X axis (left/right) = -1.0 to 1.0
ci_right_y:float = 0.0                   # Right Stick Y axis (left/right) = -1.0 to 1.0
ci_lt:float = 0.0                        # Left Trigger = 0.0 to 1.0
ci_rt:float = 0.0                        # Right Trigger = 0.0 to 1.0

# declare xbox controller input variables
armed:bool = False
throttle:float = 0.0      # between 0.0 and 1.0
pitch:float = 0.0         # between -1.0 and 1.0
roll:float = 0.0          # between -1.0 and 1.0
yaw:float = 0.0           # between -1.0 and 1.0

# Declare NonlinearTransformers for Pitch, Roll, and Yaw
nlt_pitch:tools.NonlinearTransformer = tools.NonlinearTransformer(2.0, 0.05)
nlt_roll:tools.NonlinearTransformer = tools.NonlinearTransformer(2.0, 0.05)
nlt_yaw:tools.NonlinearTransformer = tools.NonlinearTransformer(2.0, 0.10) # my deadzone is higher than the others because I have a broken right stick on my controller that often rests at around 8% in either direction




################################
##### FINAL START UP STUFF #####
################################

# Timestamps, in ticks_us, for each primary function
last_ci_check:int = time.ticks_us()            # the last time we checked for controller input via UART (received from RPi)
last_display_update:int = time.ticks_us()      # the last time we updated the SSD-1306 display





##############################
##### NOW INFINITE LOOP! #####
##############################
boot_update("Ready!")
time.sleep(1.0)
dc.page = "awaiting_ci"
print("Beginning infinite control loop!")
started_waiting_ticks_ms:int = time.ticks_ms()
try:
    while True:

        ### PERIODIC TIMESTAMP BASED THINGS BELOW ###

        # Check for control input via UART from the RPi with the controller?
        if time.ticks_diff(time.ticks_us(), last_ci_check) > 5_000:

            # check if we have any input data to receive from the xbox controller
            ba:int = uart_ci.any()
            if ba > 0:
                newdata:bytes = uart_ci.read(ba)
                rxBuffer.extend(newdata)
            
            # Do we have a line?
            while True:
                term_loc:int = rxBuffer.find("\r\n".encode())
                if term_loc != -1:

                    # update the last time we received control input from the RPi 
                    # doesn't necessarily have to be actual control input (i.e. an event happening...)
                    # can also be the "HELLO" message or a problem flag
                    ci_last_received_ticks_us = time.ticks_us() # update last received time

                    # extract the line                    
                    ThisLine:bytes = rxBuffer[0:term_loc+2] # include the \r\n at the end
                    rxBuffer = rxBuffer[len(ThisLine):] # keep the rest, trim out that line

                    # is it a problem?
                    if ThisLine == b'@\r\n': # this is 0b01000000 followed by \r\n (3 bytes), indicating there is a problem
                        print("Problem flag received from RPi! Issue with controller telemetry.")
                        dc.page = "ci_problem" # change the display controller to ci_problem for it to be displayed there is a problem
                    else: # it is good control data! So just update the control input states...
                        if ThisLine[0] & 0b01000000 > 0: # if bit 6 is a 1, that means it is a joystick (variable) input, i.e. LT/RT or joystick X/Y axes
                            id,value = tools.unpack_joystick_input(ThisLine)
                            if id == 0:
                                ci_left_x = value
                            elif id == 1:
                                ci_left_y = value
                            elif id == 2:
                                ci_right_x = value
                            elif id == 3:
                                ci_right_y = value
                            elif id == 4:
                                ci_lt = value
                            elif id == 5:
                                ci_rt = value
                        else: # if bit 6 is 0, it is a button press down
                            btn,status = tools.unpack_button_input(ThisLine)
                            if btn == 0:
                                ci_a = status
                            elif btn == 1:
                                ci_b = status
                            elif btn == 2:
                                ci_x = status
                            elif btn == 3:
                                ci_y = status
                            elif btn == 4:
                                ci_up = status
                            elif btn == 5:
                                ci_right = status
                            elif btn == 6:
                                ci_down = status
                            elif btn == 7:
                                ci_left = status
                            elif btn == 8:
                                ci_lb = status
                            elif btn == 9:
                                ci_rb = status
                            elif btn == 10:
                                ci_ls = status
                            elif btn == 11:
                                ci_rs = status
                            elif btn == 12:
                                ci_back = status
                            elif btn == 13:
                                ci_start = status
                else:
                    break

            # update last time we checked
            last_ci_check = time.ticks_us()

        # Update display?
        if time.ticks_diff(time.ticks_us(), last_display_update) > 100_000:
            dc.display()
            last_display_update = time.ticks_us()






        ### MAIN PROGRAM BELOW! ###

        # handle what to do based on what page we are on
        if dc.page == "awaiting_ci":
            if ci_last_received_ticks_us != None: # if we finally got some telemetry from the RPi with the controller via UART to confirm it is working...
                dc.page = "home" # move on!
            else: # if we haven't gotten any good telemetry yet...
                dc.seconds_waiting = int((time.ticks_ms() - started_waiting_ticks_ms)/1000) # update the seconds we have been waiting

        elif dc.page == "home": # we are on the home page
            
            # armed?
            if ci_a:
                armed = True
            elif ci_b:
                armed = False

            # other inputs
            throttle = ci_rt
            pitch = nlt_pitch.transform(ci_left_y)
            roll = nlt_roll.transform(ci_left_x)
            yaw = nlt_yaw.transform(ci_right_x)

            # plug into display controller
            dc.armed = armed
            dc.throttle = throttle
            dc.pitch = pitch
            dc.roll = roll
            dc.yaw = yaw

            # "back" button means they want to go to PID-sending area
            if ci_back:
                dc.page = "pid confirm"

        elif dc.page == "pid confirm":
            if ci_y: # confirm, yes I want to send pid settings
                dc.page = "send pid"
            elif ci_b: # go back home
                dc.page = "home"
        
        elif dc.page == "send pid":

            # completely hijack thead while sending

            # Pre-compiled PID settings payload, with the following settings:
            # pitch_kp = 4371
            # pitch_ki = 102
            # pitch_kd = 64286
            # roll_kp = 4371
            # roll_ki = 102
            # roll_kd = 64286
            # yaw_kp = 17143
            # yaw_ki = 137
            # yaw_kd = 0
            # i_limit = 350000
            # Use "pack_settings_update" function in the PC's utils.py module to pre-compile with other settings if you want to change
            pid_settings_payload:bytes = b'\x01\x11\x13\x00f\xfb\x1e\x11\x13\x00f\xfb\x1eB\xf7\x00\x89\x00\x00\x01^b\r\n'

            # attempt!
            UpdateSuccessful:bool = False
            for attempt in range(0, 5):
                send_attempt:int = attempt + 1

                # update the display
                dc.send_pid_attempt = send_attempt
                dc.send_pid_status = "Sending..."
                dc.display()

                # send it!
                uart_hc12.write(pid_settings_payload)
                time.sleep(0.25)

                # Update the dispaly
                dc.send_pid_status = "Listening..."
                dc.display()

                # wait for a moment for a response to be received
                time.sleep(3.0)

                # check - did we receive the confirmation?
                nb:int = uart_hc12.any()
                if nb > 0:
                    newdata:bytes = uart_hc12.read(nb)
                    if "SETUPOK".encode() in newdata:
                        UpdateSuccessful = True
                        break
                    else:
                        dc.send_pid_status = "No Response"
                        dc.display()
                        time.sleep(1.0)

            # did it work? Show success/error message?
            if UpdateSuccessful:
                dc.send_pid_status = "Confirmed!"
                dc.display()
                time.sleep(2.0)
            else:
                dc.send_pid_status = "FAILED!"
                dc.display()
                time.sleep(3.0)

            dc.page = "home"


        # Standard wait time
        time.sleep(0.01)


except Exception as ex:
    raise ex