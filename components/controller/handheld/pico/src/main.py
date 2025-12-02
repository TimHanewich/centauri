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
    ci_PROBLEM:bool = False                  # Flag for if there was a problem with the controller input being received
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
                    rxBuffer = rxBuffer[len(term_loc):] # keep the rest, trim out that line

                    # is it a problem?
                    if ThisLine == b'@\r\n': # this is 0b010000 followed by \r\n (3 bytes), indicating there is a problem
                        dc.page = "ci_problem" # change the display controller to ci_problem for it to be displayed there is a problem
                    else: # it is good control data!
                        inputs:dict = tools.unpack_controls(ThisLine) # will return None if there was a problem
                        if inputs != None:
                            ci_last_received_ticks_us = time.ticks_us()
                            ci_ls = inputs["ls"]
                            ci_rs = inputs["rs"]
                            ci_back = inputs["back"]
                            ci_start = inputs["start"]
                            ci_a = inputs["a"]
                            ci_b = inputs["b"]
                            ci_x = inputs["x"]
                            ci_y = inputs["y"]
                            ci_up = inputs["up"]
                            ci_right = inputs["right"]
                            ci_down = inputs["down"]
                            ci_left = inputs["left"]
                            ci_lb = inputs["lb"]
                            ci_rb = inputs["rb"]
                            ci_left_x = inputs["left_x"]
                            ci_left_y = inputs["left_y"]
                            ci_right_x = inputs["right_x"]
                            ci_right_y = inputs["right_y"]
                            ci_lt = inputs["lt"]
                            ci_rt = inputs["rt"]
                else:
                    break
                
            await asyncio.sleep(0.025) # 40 times per second

    async def continuous_display() -> None:
        while True:
            dc.display()
            await asyncio.sleep(0.1) # 10 Hz

    async def MAINCONTROL() -> None:

        # first - wait for controller input until it comes in via UART
        started_waiting_ticks_ms:int = time.ticks_ms()
        while ci_last_received_ticks_us == None:
            dc.page = "awaiting_ci"
            dc.seconds_waiting = int((time.ticks_ms() - started_waiting_ticks_ms)/1000)
            await asyncio.sleep(0.25)

        # We are good to go now! So switch to home screen
        dc.page = "home"

        # declare xbox controller input variables
        armed:bool = False
        throttle:float = 0.0      # between 0.0 and 1.0
        pitch:float = 0.0         # between -1.0 and 1.0
        roll:float = 0.0          # between -1.0 and 1.0
        yaw:float = 0.0           # between -1.0 and 1.0

        while True:

            # first, check for problems
            if not ci_PROBLEM:
                if dc.page == "home": # we are on the home page
                    
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