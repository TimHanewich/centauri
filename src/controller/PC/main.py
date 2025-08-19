import pygame
import time
import display
import asyncio
import rich.table
import rich.console
import rich.live
import serial
import tools

async def main() -> None:

    # say hello
    print("Hello and welcome to the Centauri control system.")


    # Initialize pygame and joystick module
    print("Initializing pygame for controller reads...")
    pygame.init()
    pygame.joystick.init()

    # count how many controllers (joysticks) are connected
    num_joysticks = pygame.joystick.get_count()
    print("Number of connected controllers: " + str(num_joysticks))
    if num_joysticks == 0:
        print("No controllers connected! You must connect one before proceeding.")
        exit()

    # loop through each controller
    for i in range(num_joysticks):
        tjs = pygame.joystick.Joystick(i)
        tjs.init()
        print("Joystick " + str(i) + ": " + tjs.get_name())

    # select the controller that will be used
    controller = pygame.joystick.Joystick(0)
    controller.init()
    print("Controller #0, '" + controller.get_name() + "' will be used.")

    # ask what serial peripheral path to use for communications
    print()
    print("Attempt to open serial port will happen IMMEDIATELY upon you hitting enter")
    ser_port:str = input("Serial port of your transceiver (i.e. 'COM3' or '/dev/ACM0'): ")
    print("Will use serial '" + ser_port + "'")
    print()

    # try to establish comms with serial device
    print("Opening serial port...")
    ser:serial.Serial = serial.Serial(port=ser_port, baudrate=9600, timeout=5)
    if ser.in_waiting > 0:
        print(str(len(ser.in_waiting)) + " bytes in recv buffer, clearing now.")
        ser.read(ser.in_waiting) # clear out buffer
    PING_MSG:str = "TRAN" + "PING" + "\r\n"
    print("Sending ping message...")
    ser.write(PING_MSG.encode())
    print("Waiting for response...")
    time.sleep(0.25)
    if ser.in_waiting == 0:
        print("Transceiver did not respond to ping. Are you sure it is connected and working properly?")
        ser.close()
        exit()
    response:bytes = ser.read(ser.in_waiting)
    print("Response of " + str(len(response)) + " bytes received from transceiver.")
    if response == "TRANPONG\r\n".encode(): # the expected response
        print("Transceiver ping successful! It is operating normally.")
    else:
        print("Transceiver responded abnormally. Are you sure it is working correctly? Response: " + str(response))
        ser.close()
        exit()

    # Send a ping to the drone now to confirm it is on and operating

    # Send a config packet to the drone to set settings

    # set up control inputs
    armed:bool = False
    mode:bool = False
    throttle:float = 0.0 # 0.0 to 1.0
    pitch:float = 0.0
    roll:float = 0.0
    yaw:float = 0.0

    # set up system info variables
    packets_sent:int = 0
    packets_received:int = 0
    packets_last_received_ms_ago:int = 9999

    # set up continous Xbox controller read function
    async def continuous_read_xbox() -> None:

        # declare non-local variables from main we will be accessing
        nonlocal armed
        nonlocal mode
        nonlocal throttle
        nonlocal pitch
        nonlocal roll
        nonlocal yaw
        
        # infinite loop of reading
        while True:

            # handle changes in input state on the Xbox controller
            for event in pygame.event.get():
                if event.type == pygame.JOYAXISMOTION:
                    if event.axis == 5: # right trigger
                        throttle = (event.value + 1) / 2
                    elif event.axis == 0: # left stick X axis (left/right)
                        roll = event.value
                    elif event.axis == 1: # left stick Y axis (up/down)
                        pitch = event.value # pushing the left stick forward will result in a NEGATIVE value. While this may seem incorrect at first, it is actually correct... pushing the left stick forward should prompt the quadcopter to pitch down (forward), hence it should be negative!
                    elif event.axis == 2: # right stick X axis (left/right)
                        yaw = event.value
                    else:
                        #print("Axis '" + str(event.axis) + "': " + str(event.value))
                        pass
                elif event.type == pygame.JOYBUTTONDOWN:
                    if event.button == 0: # A
                        armed = True
                    elif event.button == 1: # B
                        armed = False
                    elif event.button == 4: # LB
                        mode = False # rate mode
                    elif event.button == 5: # RB
                        mode = True # angle mode
                    else:
                        #print("Button pressed: " + str(event.button))
                        pass
            
            # wait a moment
            await asyncio.sleep(0.05)
        
    # set up continuous display function
    async def continuous_display() -> None:

        # declare variables from main we will be using
        nonlocal armed
        nonlocal mode
        nonlocal throttle
        nonlocal pitch
        nonlocal roll
        nonlocal yaw
        nonlocal packets_sent

        # display with live
        with rich.live.Live(refresh_per_second=60, screen=True) as l: # the refresh_per_second sets the upper limit for refresh rate
            while True:

                # prepare to print with display packet
                dp:display.DisplayPack = display.DisplayPack()
                dp.armed = armed
                dp.mode = mode
                dp.throttle = throttle
                dp.pitch = pitch
                dp.roll = roll
                dp.yaw = yaw
                dp.packets_sent = packets_sent
                
                # get table
                tbl = display.construct(dp)

                # update live
                l.update(tbl)

                # wait
                await asyncio.sleep(0.01)

    # set up continuous radio sending
    async def continuous_radio_tx() -> None:

        # declare variables from main we will be using
        nonlocal armed
        nonlocal mode
        nonlocal throttle
        nonlocal pitch
        nonlocal roll
        nonlocal yaw
        nonlocal packets_sent
        nonlocal ser # serial port

        while True:

            # pack into control packet
            ToSend:bytes = tools.pack_control_packet(armed, mode, throttle, pitch, roll, yaw)
            
            # send it
            ser.write(bytes(ToSend))
            packets_sent = packets_sent + 1

            # wait
            await asyncio.sleep(0.02) # 50 Hz

    # we are all set and ready to go. Confirm.
    print()
    input("All set and ready to go! Enter to continue.")

    # get all threads going
    task_read_xbox = asyncio.create_task(continuous_read_xbox())
    task_display = asyncio.create_task(continuous_display())
    task_radio_tx = asyncio.create_task(continuous_radio_tx())
    await asyncio.gather(task_read_xbox, task_display, task_radio_tx) # infinitely wait for all to finish (which will never happen since they are infinitely running)


# run main program via asyncio
asyncio.run(main())