import pygame
import time
import display
import asyncio
import rich.table
import rich.console
import rich.live
from rich.console import Console
from rich.prompt import Prompt
import serial
import tools
import sys

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
    ser_port:str = input("Serial port of your transceiver (i.e. 'COM3' or '/dev/ttyACM0'): ")
    print("Will use serial '" + ser_port + "'")
    print()

    # try to establish comms with serial device
    print("Opening serial port...")
    ser:serial.Serial = None
    try:
        ser:serial.Serial = serial.Serial(port=ser_port, baudrate=9600, timeout=5)
    except Exception as ex:
        print("Error while trying to open port!")
        print("Error message: " + str(ex))
        print("Exiting script...")
        exit()
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
    if "TRANPONG\r\n".encode() in response: # the expected response
        print("Transceiver ping successful! It is operating normally.")
    else:
        print("Transceiver did not respond with TRANSPONG, confirming it is alive. Are you sure it is working correctly? Response we received from it: " + str(response))
        ser.close()
        exit()

    # declare default settings
    idle_throttle:float = 0.10   # X% throttle is idle
    max_throttle:float = 0.25    # X% throttle is the max

    # print settings
    print()
    Console.print("[underline]Settings[/]")
    Console.print("Idle Throttle: [blue]" + str(round(idle_throttle * 100, 0)) + "%[/]")
    Console.print("Max Throttle: [blue]" + str(round(max_throttle * 100, 0)) + "%[/]")
    print()
    
    # Confirm settings
    confirmed:str = Prompt.ask("Do these settings look good?", choices=["Yes","No"], show_choices=True)
    if not confirmed:
        print("Please update the code file.")
        exit()

    # Send a ping to the drone now to confirm it is on and operating


    # set up control input variables we will track, display in console, and then interpret and transform before sending to drone in control packet
    armed:bool = False       # armed is being tracked here not as a variable we will directly pass on to the quadcopter, but rather a variable we will use to know if we should be transmitting at least the minimum throttle (when armed) or 0% throttle
    mode:bool = False        # UNUSED for right now! Only rate mode works. Rate Mode = False, Angle Mode = True
    throttle:float = 0.0     # between 0.0 and 1.0
    pitch:float = 0.0        # between -1.0 and 1.0
    roll:float = 0.0         # between -1.0 and 1.0
    yaw:float = 0.0          # between -1.0 and 1.0

    # set up status variables we will get from the drone (and display in the console!): system status
    vbat:float = 0.0 # volts
    tf_luna_distance:int = 0 # in cm
    tf_luna_strength:int = 0
    altitude:float = 0.0 # from BMP180, in meters
    heading:int = 0 # in degrres

    # set up status variables we will get from the drone (and display in the console!): control status
    pitch_angle:int = 0 # in degrees
    roll_angle:int = 0 # in degrees
    pitch_rate:int = 0 # in degrees per second
    roll_rate:int = 0 # in degrees per second
    yaw_rate:int = 0 # in degrees per second
    m1_throttle:int = 0 # 0-100 (%)
    m2_throttle:int = 0 # 0-100 (%)
    m3_throttle:int = 0 # 0-100 (%)
    m4_throttle:int = 0 # 0-100 (%)


    # set up system info variables
    packets_sent:int = 0
    packets_received:int = 0
    packets_last_received_at:float = None # timestamp of last received, in seconds (time.time()). Start with None to indicate we have NOT received one yet.

    # For Display: set up messages received from drone
    drone_messages:list[display.Message] = []

    # set up continous Xbox controller read function
    async def continuous_read_xbox() -> None:

        # declare non-local variables from main we will be accessing
        nonlocal armed
        nonlocal mode
        nonlocal throttle
        nonlocal pitch
        nonlocal roll
        nonlocal yaw

        # determine what the yaw axis ID is (right stick X, horizontal, axis)
        # it is different based on what OS you are on I find
        # On Windows, right stick X axis (horizontal) = 2
        # On Linux, right stick X axis (horizontal) = 3
        right_stick_x_axis_id:int = 2 # default to windows
        if sys.platform.startswith("linux"): # if we are on linux
            right_stick_x_axis_id = 3 # set to3
        
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
                    elif event.axis == right_stick_x_axis_id: # right stick X axis (left/right)
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

        # display with live
        with rich.live.Live(refresh_per_second=60, screen=True) as l: # the refresh_per_second sets the upper limit for refresh rate
            while True:

                # prepare to print with display packet
                dp:display.DisplayPack = display.DisplayPack()

                # plug in basic telemetry info
                dp.packets_sent = packets_sent
                dp.packets_received = packets_received
                if packets_last_received_at != None:
                    dp.packet_last_received_ago_ms = int((time.time() - packets_last_received_at) * 1000)
                else:
                    dp.packet_last_received_ago_ms = None

                # plug in control variables
                dp.armed = armed
                dp.mode = mode
                dp.throttle = throttle
                dp.pitch = pitch
                dp.roll = roll
                dp.yaw = yaw
                
                # plug in drone status variables: system status
                dp.drone_battery = vbat
                dp.tf_luna_distance = tf_luna_distance
                dp.tf_luna_strength = tf_luna_strength
                dp.altitude = altitude
                dp.heading = heading

                # plug in drone status variables: control status
                dp.M1_throttle = m1_throttle
                dp.M2_throttle = m2_throttle
                dp.M3_throttle = m3_throttle
                dp.M4_throttle = m4_throttle
                dp.pitch_rate = pitch_rate
                dp.roll_rate = roll_rate
                dp.yaw_rate = yaw_rate
                dp.pitch_angle = pitch_angle
                dp.roll_angle = roll_angle

                # plug in drone messages
                dp.messages = drone_messages
                
                # get table
                tbl = display.construct(dp)

                # update live
                l.update(tbl)

                # wait
                await asyncio.sleep(0.01)

    # set up continuous radio sending
    async def continuous_radio_tx() -> None:

        # declare variables from main we will be updating
        nonlocal packets_sent

        while True:

            # if we are armed, calculate what the scaled throttle will be
            # it will be idle throttle + (throttle input * (max throttle - min throttle))
            # (scaled within idle throttle and max throttle range)

            if armed:
                throttle_to_send:float = idle_throttle + ((max_throttle - idle_throttle) * throttle) # scale within range, if armed
                ToSend:bytes = tools.pack_control_packet(throttle_to_send, pitch, roll, yaw) # pack into bytes
                ser.write(ToSend + "\r\n".encode()) # send it via HC-12 by sending it to the transceiver over the serial line
                packets_sent = packets_sent + 1
                await asyncio.sleep(0.05) # 20 Hz
            else:
                ToSend:bytes = tools.pack_control_packet(0.0, 0.0, 0.0, 0.0) # pack all 0 inputs
                ser.write(ToSend + "\r\n".encode())
                ser.write(ToSend + "\r\n".encode()) # send it via HC-12 by sending it to the transceiver over the serial line
                packets_sent = packets_sent + 1
                await asyncio.sleep(0.5) # 2 Hz

    # set up continuous radio rx (through tranceiver)
    async def continuous_radio_rx() -> None:
        """Handles all received data from the transceiver via the USB (the transceiver passes along data it receives via the HC-12)"""

        # declare nonlocal variables we will be modifying
        nonlocal packets_received
        nonlocal packets_last_received_at
        nonlocal vbat # drone's battery level
        nonlocal tf_luna_distance
        nonlocal tf_luna_strength
        nonlocal altitude
        nonlocal heading
        nonlocal pitch_angle
        nonlocal roll_angle
        nonlocal pitch_rate
        nonlocal roll_rate
        nonlocal yaw_rate
        nonlocal m1_throttle
        nonlocal m2_throttle
        nonlocal m3_throttle
        nonlocal m4_throttle

        # declare rxBuffer of all data received from transceiver through the USB serial line
        rxBuffer:bytearray = bytearray()

        # continuously monitor and receive new data from the serial port (from transceiver)
        while True:

            # read data if any is available!
            if ser.in_waiting > 0: # if we have data available
                data:bytes = ser.read(ser.in_waiting) # read the available data
                rxBuffer.extend(data)
                
            # handle data if we have any full lines in there
            while "\r\n".encode() in rxBuffer:

                # get the line
                loc:int = rxBuffer.find("\r\n".encode())
                ThisLine:bytes = rxBuffer[0:loc+2] # include the \r\n at the end (why we +2)
                rxBuffer = rxBuffer[loc+2:] # remove the line

                # increment packets received and mark the receiving timestamp
                packets_received = packets_received + 1
                packets_last_received_at = time.time()

                # Handle the line based on what it is
                if ThisLine[0] & 0b00000011 == 0b00000000: # if bit 0 and bit 1 of the first byte (packet header) are both 0's, it is a control status packet
                    ControlStatus:dict = tools.unpack_control_status(ThisLine)
                    if ControlStatus != None: # it would return None if the checksum was not correct (data transmission issue)
                        m1_throttle = ControlStatus["m1_throttle"]
                        m2_throttle = ControlStatus["m2_throttle"]
                        m3_throttle = ControlStatus["m3_throttle"]
                        m4_throttle = ControlStatus["m4_throttle"]
                        pitch_rate = ControlStatus["pitch_rate"]
                        roll_rate = ControlStatus["roll_rate"]
                        yaw_rate = ControlStatus["yaw_rate"]
                        pitch_angle = ControlStatus["pitch_angle"]
                        roll_angle = ControlStatus["roll_angle"]
                elif ThisLine[0] & 0b00000010 == 0 and ThisLine[0] & 0b00000001 > 0: # bit 0 is occupied, bit 1 is not = it is a SYSTEM STATUS!
                    SystemStatus:dict = tools.unpack_system_status(ThisLine)
                    vbat = SystemStatus["battery_voltage"]
                    tf_luna_distance = SystemStatus["tf_luna_distance"]
                    tf_luna_strength = SystemStatus["tf_luna_strength"]
                    altitude = SystemStatus["altitude"]
                    heading = SystemStatus["heading"]
                elif ThisLine[0] & 0b00000010 > 0 and ThisLine[0] & 0b00000001 == 0: # bit 1 is occupied but bit 0 is not = it is a special packet (free text)
                    msg:str = tools.unpack_special_packet(ThisLine)
                    drone_messages.append(display.Message(msg, time.time()))
                else:
                    drone_messages.append(display.Message("NFD: Unknown received data.", time.time())) # NDF short for "Not from drone"
            
            # sleep
            await asyncio.sleep(0.05) # 20 Hz, faster than the 10 Hz the drone will send it at


    # we are all set and ready to go. Confirm.
    print()
    input("All set and ready to go! Enter to continue.")

    # get all threads going
    task_read_xbox = asyncio.create_task(continuous_read_xbox())
    task_display = asyncio.create_task(continuous_display())
    task_radio_tx = asyncio.create_task(continuous_radio_tx())
    task_radio_rx = asyncio.create_task(continuous_radio_rx())
    await asyncio.gather(task_read_xbox, task_display, task_radio_tx, task_radio_rx) # infinitely wait for all to finish (which will never happen since they are infinitely running)


# run main program via asyncio
asyncio.run(main())