import time
import machine
import ssd1306
import asyncio
import tools
from display import Display

async def main() -> None:

    # Set up the SSD1306 OLED
    i2c = machine.I2C(1, sda=machine.Pin(14), scl=machine.Pin(15))
    if 60 not in i2c.scan():
        print("SSD1306 not detected! Exiting.")
        exit()
    oled = ssd1306.SSD1306_I2C(128, 64, i2c)

    # declare display
    dc:Display = Display(oled)

    # display the centauri graphic during loading
    dc.page = "logo"
    dc.display()
    time.sleep(2.0) # wait for 2 seconds

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

    async def continuous_xbox_read() -> None:

        # declare nonlocal (shared) variables
        nonlocal ci_last_received_ticks_us
        nonlocal ci_ls
        nonlocal ci_rs
        nonlocal ci_back
        nonlocal ci_start
        nonlocal ci_a
        nonlocal ci_b
        nonlocal ci_x
        nonlocal ci_y
        nonlocal ci_up
        nonlocal ci_right
        nonlocal ci_down
        nonlocal ci_left
        nonlocal ci_lb
        nonlocal ci_rb
        nonlocal ci_left_x
        nonlocal ci_left_y
        nonlocal ci_right_x
        nonlocal ci_right_y
        nonlocal ci_lt
        nonlocal ci_rt

        # Set up UART to receive controller input data from the RPi
        uart = machine.UART(0, baudrate=9600, tx=machine.Pin(16), rx=machine.Pin(17))
        if uart.any(): # clear out the rxbuffer
            uart.read(uart.any())
        rxBuffer:bytearray = bytearray()
        
        while True:
            
            # check if we have any input data to receive from the xbox controller
            ba:int = uart.any()
            if ba > 0:
                rxBuffer.extend(uart.read(ba))
            
            # Do we have a line?
            while True:
                term_loc:int = rxBuffer.find("\r\n".encode())
                if term_loc != -1:

                    # extract the line                    
                    ThisLine:bytes = rxBuffer[0:term_loc+2] # include the \r\n at the end
                    rxBuffer = rxBuffer[len(ThisLine):] # keep the rest, trim out that line

                    # is it a problem?
                    if ThisLine == b'@\r\n': # this is 0b01000000 followed by \r\n (3 bytes), indicating there is a problem
                        print("Problem flag received from RPi! Issue with controller telemetry.")
                        dc.page = "ci_problem" # change the display controller to ci_problem for it to be displayed there is a problem
                    else: # it is good control data! So just update the control input states...
                        ci_last_received_ticks_us = time.ticks_us() # update last received time

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
                
            await asyncio.sleep(0.025) # 40 times per second

    async def continuous_display() -> None:
        while True:
            dc.display()
            await asyncio.sleep(0.1) # 10 Hz

    async def MAINCONTROL() -> None:

        # declare xbox controller input variables
        armed:bool = False
        throttle:float = 0.0      # between 0.0 and 1.0
        pitch:float = 0.0         # between -1.0 and 1.0
        roll:float = 0.0          # between -1.0 and 1.0
        yaw:float = 0.0           # between -1.0 and 1.0

        # start on awaiting_ci page as that is what we do first: verify telemetry comes in
        started_waiting_ticks_ms:int = time.ticks_ms()
        dc.page = "awaiting_ci"

        # Infinite loop handling what to do in each "mode" we are on, 
        # with that "mode" often indicated by what page we are on
        while True:

            # handle what to do based on what page we are on
            if dc.page == "awaiting_ci":
                if ci_last_received_ticks_us != None: # if we finally go telemetry from the controller...
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
                pitch = ci_left_y
                roll = ci_left_x
                yaw = ci_right_x

                # plug into display controller
                dc.armed = armed
                dc.throttle = throttle
                dc.pitch = pitch
                dc.roll = roll
                dc.yaw = yaw

            # standard wait time
            await asyncio.sleep(0.10)

    # get all threads going
    task_read_xbox = asyncio.create_task(continuous_xbox_read())
    task_display = asyncio.create_task(continuous_display())
    task_MAINCONTROL = asyncio.create_task(MAINCONTROL())
    await asyncio.gather(task_read_xbox, task_display, task_MAINCONTROL)

asyncio.run(main())