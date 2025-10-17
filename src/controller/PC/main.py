# hide the "Welcome to the Pygame community..." message when we import pygame
import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"

import pygame
import time
import display
import asyncio
import rich.live
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
import serial
import tools
import sys
import keyboard

async def main() -> None:

    # initialization settings (can be altered for testing)
    controller_required:bool = False
    transceiver_required:bool = False

    # create a console instance from the Rich library so we can print with fancy font and stuff
    console = Console()

    # say hello
    print()
    console.print("[bold][blue]Hello and welcome to the Centauri control system.[/bold][/blue]")
    console.print("[italic]github.com/TimHanewich/centauri[/italic]")
    print()

    # Initialize pygame and joystick module
    console.print("[u]Controller Setup[/u]")
    print("Initializing pygame for controller reads...")
    pygame.init()
    pygame.joystick.init()

    # count how many controllers (joysticks) are connected
    num_joysticks = pygame.joystick.get_count()
    print("Number of connected controllers: " + str(num_joysticks))
    if controller_required and num_joysticks == 0:
        print("No controllers connected! You must connect one before proceeding.")
        exit()

    # loop through each controller
    for i in range(num_joysticks):
        tjs = pygame.joystick.Joystick(i)
        tjs.init()
        print("Joystick " + str(i) + ": " + tjs.get_name())

    # select the controller that will be used
    controller = None
    if num_joysticks > 0:
        controller = pygame.joystick.Joystick(0)
        controller.init()
        print("Controller #0, '" + controller.get_name() + "' will be used.")

    # ask what serial peripheral path to use for communications
    print()
    console.print("[u]Transceiver Setup[/u]")
    print("Attempt to open serial port will happen IMMEDIATELY upon you hitting enter")
    ser_port:str = input("Serial port of your transceiver (i.e. 'COM3' or '/dev/ttyUSB0' or '/dev/ttyACM0'): ")

    # set up serial and begin setup comms with drone
    ser:serial.Serial = None
    if ser_port == "": # they left it blank
        if transceiver_required:
            print("You did not provide a valid serial port! Exiting...")
            exit()
        else:
            print("Skipping serial connection to transceiver as it is not required.")
    else: # they provided something
        print("Will use serial '" + ser_port + "'")
        print()

        # Open serial port
        print("Opening serial port...")
        try:
            ser:serial.Serial = serial.Serial(port=ser_port, baudrate=115200, timeout=5)
        except Exception as ex:
            print("Error while trying to open port!")
            print("Error message: " + str(ex))
            print("Exiting script...")
            exit()
        if ser.in_waiting > 0:
            print(str(ser.in_waiting) + " bytes in recv buffer, clearing now.")
            ser.read(ser.in_waiting) # clear out buffer
        PING_MSG:str = "TRAN" + "PING" + "\r\n"
        print("Sending ping message...")
        ser.write(PING_MSG.encode())
        print("Waiting for response...")
        time.sleep(1.0)
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

        # Send a ping to the drone now to confirm it is on and operating
        print()
        console.print("[u]Drone Contact[/u]")
        print("Now attempting contact with drone...")
        started_at:float = time.time()
        wait_for_seconds:float = 10.0
        drone_ponged:bool = False
        ping_attempts:int = 0
        PongBuffer:bytearray = bytearray()
        while (time.time() - started_at) < wait_for_seconds and drone_ponged == False:

            # send a ping
            print("Sending ping attempt # " + str(ping_attempts + 1) + "...")
            ser.write("TIMHPING\r\n".encode()) # intended to be deliverd to the drone, passing THROUGH the transceiver
            ping_attempts = ping_attempts + 1

            # wait for a response
            time.sleep(1.0)

            # receive if there are any
            BytesAvailable:int = ser.in_waiting
            if BytesAvailable > 0:
                PongBuffer.extend(ser.read(BytesAvailable))
                print(str(BytesAvailable) + " bytes received.")
            else:
                print("No bytes received.")

            # check
            if "TIMHPONG\r\n".encode() in PongBuffer:
                drone_ponged = True
                print("PONG received!")
                break
            else:
                print("PONG not received yet...")
        if drone_ponged == False:
            print("Drone never ponged back!")
            exit()

    # set up control input variables we will track, display in console, and then interpret and transform before sending to drone in control packet
    armed:bool = False       # armed is being tracked here not as a variable we will directly pass on to the quadcopter, but rather a variable we will use to know if we should be transmitting at least the minimum throttle (when armed) or 0% throttle
    mode:bool = False        # UNUSED for right now! Only rate mode works. Rate Mode = False, Angle Mode = True
    throttle:float = 0.0     # between 0.0 and 1.0
    pitch:float = 0.0        # between -1.0 and 1.0
    roll:float = 0.0         # between -1.0 and 1.0
    yaw:float = 0.0          # between -1.0 and 1.0

    # Set up flight control variables, with defaults
    # these are the settings that will live on the drone, thus we will have to transmit them later
    idle_throttle:float = 0.08   # X% throttle is idle
    max_throttle:float = 0.25    # X% throttle is the max
    pitch_kp:int = 2000
    pitch_ki:int = 0
    pitch_kd:int = 0
    roll_kp:int = 2000
    roll_ki:int = 0
    roll_kd:int = 0
    yaw_kp:int = 2000
    yaw_ki:int = 0
    yaw_kd:int = 0
    i_limit:int = 0
    pid_master_multiplier:float = 1.00 # increases/decreases all PID parameters proportionally. This is great for keeping the same proportions but increasing/decreasing responsiveness

    # set up status variables we will get from the drone (and display in the console!): system status
    vbat:float = 0.0 # volts

    # set up status variables we will get from the drone (and display in the console!): control status
    pitch_angle:int = 0 # in degrees
    roll_angle:int = 0 # in degrees
    pitch_rate:int = 0 # in degrees per second
    roll_rate:int = 0 # in degrees per second
    yaw_rate:int = 0 # in degrees per second

    # set up system info variables
    packets_sent:int = 0
    packets_received:int = 0
    packets_last_received_at:float = None # timestamp of last received, in seconds (time.time()). Start with None to indicate we have NOT received one yet.

    # For Display: set up messages received from drone
    drone_messages:list[display.Message] = []

    # set up settings update function
    def update_drone_settings() -> None:
        """Collects new settings values and then transmits them to the drone."""

        # declare global variables
        nonlocal idle_throttle
        nonlocal max_throttle
        nonlocal pitch_kp
        nonlocal pitch_ki
        nonlocal pitch_kd
        nonlocal roll_kp
        nonlocal roll_ki
        nonlocal roll_kd
        nonlocal yaw_kp
        nonlocal yaw_ki
        nonlocal yaw_kd
        nonlocal i_limit
        nonlocal pid_master_multiplier

        # ask if they want to update settings continuously until they are right
        while True:

            # Calculate the EFFECTIVE PID values (using PID multiplier)
            pitch_kp_eff:int = int(pitch_kp * pid_master_multiplier)
            pitch_ki_eff:int = int(pitch_ki * pid_master_multiplier)
            pitch_kd_eff:int = int(pitch_kd * pid_master_multiplier)
            roll_kp_eff:int = int(roll_kp * pid_master_multiplier)
            roll_ki_eff:int = int(roll_ki * pid_master_multiplier)
            roll_kd_eff:int = int(roll_kd * pid_master_multiplier)
            yaw_kp_eff:int = int(yaw_kp * pid_master_multiplier)
            yaw_ki_eff:int = int(yaw_ki * pid_master_multiplier)
            yaw_kd_eff:int = int(yaw_kd * pid_master_multiplier)

            # print current settings
            console.print("[blue][underline]----- SETTINGS UPDATE TO SEND -----[/blue][/underline]")
            print()
            console.print("[u]Throttle Settings[/u]")
            console.print("Idle Throttle: [blue]" + str(round(idle_throttle * 100, 0)) + "%[/blue]")
            console.print("Max Throttle: [blue]" + str(round(max_throttle * 100, 0)) + "%[/blue]")
            print()
            console.print("[u]PID Settings[/u]")
            console.print("PID Master Multiplier: " + str(round(pid_master_multiplier, 2)))
            console.print("I Limit: [blue]" + format(i_limit, ",") + "[/blue]")
            pid_tbl:Table = Table()
            pid_tbl.add_column("Axis")
            pid_tbl.add_column("Raw Gain")
            pid_tbl.add_column("Effective Gain")
            pid_tbl.add_row("Pitch kP", format(pitch_kp, ","), format(pitch_kp_eff, ","))
            pid_tbl.add_row("Pitch kI", format(pitch_ki, ","), format(pitch_ki_eff, ","))
            pid_tbl.add_row("Pitch kD", format(pitch_kd, ","), format(pitch_kd_eff, ","))
            pid_tbl.add_row("Roll kP", format(roll_kp, ","), format(roll_kp_eff, ","))
            pid_tbl.add_row("Roll kI", format(roll_ki, ","), format(roll_ki_eff, ","))
            pid_tbl.add_row("Roll kD", format(roll_kd, ","), format(roll_kd_eff, ","))
            pid_tbl.add_row("Yaw kP", format(yaw_kp, ","), format(yaw_kp_eff, ","))
            pid_tbl.add_row("Yaw kI", format(yaw_ki, ","), format(yaw_ki_eff, ","))
            pid_tbl.add_row("yaw kD", format(yaw_kd, ","), format(yaw_kd_eff, ","))
            print()

            # Want to change?
            print("Do you want to change these?")
            console.print("[blue][bold]1[/blue][/bold] - Update these settings before sending to drone")
            console.print("[blue][bold]2[/blue][/bold] - Adjust only PID Master Multiplier (make a proportional change)")
            console.print("[blue][bold]3[/blue][/bold] - Look good! Let's send them.")
            display.flush_input() # flush input right before asking so the "s" that was just pressed in does not show
            wanttodo:str = Prompt.ask("What do you want to do?", choices=["1", "2"], show_choices=True)
            if wanttodo == "1": # update
                
                print("Okay, let's collect the new values.")

                # collect idle and max until it is valid!
                while True:
                    idle_throttle = tools.ask_float("Idle Throttle")
                    max_throttle = tools.ask_float("Max Throttle")

                    # settings validation
                    if max_throttle <= idle_throttle: 
                        print("Max Throttle must be GREATER THAN idle throttle!")
                        print("Try again please.")
                    else:
                        break

                # Collect new settings
                pitch_kp = tools.ask_integer("Pitch kP")
                pitch_ki = tools.ask_integer("Pitch kI")
                pitch_kd = tools.ask_integer("Pitch kD")
                roll_kp = tools.ask_integer("Roll kP")
                roll_ki = tools.ask_integer("Roll kI")
                roll_kd = tools.ask_integer("Roll kD")
                yaw_kp = tools.ask_integer("Yaw kP")
                yaw_ki = tools.ask_integer("Yaw kI")
                yaw_kd = tools.ask_integer("Yaw kD")
                i_limit = tools.ask_integer("I Limit")
                print()

            elif wanttodo == "2": # update only PID Master Multiplier
                npmm:float = tools.ask_float("New PID Master Multiplier to use")
                pid_master_multiplier = npmm
            elif wanttodo == "3": # send to drone as is
                print("Using those settings values!")
                break # break out of the infinite loop of asking if the settings look good
            else:
                console.print("[red]Invalid choice.[/red]")

        # Send a settings update (PID settings)
        if ser != None:
            print()
            print("Will now send out PID update!")

            # try a certain number of times
            confirmed:bool = False
            attempts:int = 0
            while confirmed == False and attempts < 5:

                console.print("[u]PID Update Attempt # " + str(attempts+1) + "[/u]")

                # pack it
                print("Packing PID updates...")
                ToSend:bytes = tools.pack_settings_update(pitch_kp, pitch_ki, pitch_kd, roll_kp, roll_ki, roll_kd, yaw_kp, yaw_ki, yaw_kd, i_limit)

                # send it
                print("Sending PID updates...")
                ser.write(ToSend + "\r\n".encode())
                attempts = attempts + 1

                # wait
                print("Settings packet sent!")
                print("Waiting a moment for it to register.")
                time.sleep(1.5)

                # handle
                print("Checking for settings update confirmation...")
                if ser.in_waiting == 0:
                    print("No data at all received from drone. Was expecting settings update confirmation.")
                else: # There is some data available to read. Is it the confirmation?
                    recv:bytes = ser.read(ser.in_waiting) # read all available
                    if "SETUPOK".encode() in recv: # it should send "SETUPOK" as a special packet (plain text)
                        print("Settings update confirmation received from drone!")
                        confirmed = True
                        input("Return to continue.")
                    else:
                        print("Drone sent back " + str(len(recv)) + " bytes but it wasn't a successful settings update.")

            # if it just straight up did not work, say so
            if confirmed == False: # it never confirmed, which means we went past the number of tries
                print("After a number of attempts, the drone did NOT confirm the PID settings update.")
                print("There is a good chance it did NOT update the settings values, so be careful!")
                input("Return to continue.")
            
        else:
            print("Transceiver not set up, so skipping sending it out!")
            input("Return to continue.")

    # ask if, before starting, they want to do a settings update
    print()
    print("Before flying, do you want to send a settings update to the drone?")
    print("This is recommended for safety reasons.")
    sendsettingsupdate:str = Prompt.ask("Send settings update now?", choices=["y", "n"], show_choices=True)
    if sendsettingsupdate == "y":
        print()
        update_drone_settings()
    else:
        print("Skipping settings update.")







    #############################
    ##### CO-ROUTINES BELOW #####
    #############################

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
            try:
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
            except: # if it fails for some reason (i.e. glitch or xbox controller unplugged?), unarm!
                armed = False
                throttle = 0.0
                pitch = 0.0
                roll = 0.0
                yaw = 0.0
            
            # wait a moment
            await asyncio.sleep(0.05)
        
    # set up continuous display function
    async def continuous_display() -> None:

        # display with live
        with rich.live.Live(refresh_per_second=60, screen=True) as l: # the refresh_per_second sets the upper limit for refresh rate
            while True:

                # check if we should engage menu modes
                if armed == False: # only allow for entering into menus if NOT armed. If in flight mode, it isn't allowed for safety reasons.
                    if keyboard.is_pressed("s"): # SETTINGS MODE
                        
                        # Wait until S is depressed to enter settings
                        l.stop() # stop the animation
                        display.cls()
                        print("Stop pressing S to enter settings.")
                        while keyboard.is_pressed("s"):
                            time.sleep(0.1)
                        display.cls()

                        # trigger collection and transmitting of settings data to drone
                        update_drone_settings()

                        # restart
                        l.start()

                # prepare to print with display packet
                dp:display.DisplayPack = display.DisplayPack()

                # plug in basic telemetry info
                dp.uptime_seconds = time.time() - booted    # uptime of the system, in seconds (current time minus the booted timestamp)
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

                # plug in drone telemetry variables
                dp.drone_battery = vbat
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
            if armed:
                throttle_to_send:float = idle_throttle + ((max_throttle - idle_throttle) * throttle) # scale within range, if armed
                ToSend:bytes = tools.pack_control_packet(throttle_to_send, pitch, roll, yaw) # pack into bytes
                if ser != None:
                    ser.write(ToSend + "\r\n".encode()) # send it via HC-12 by sending it to the transceiver over the serial line
                    packets_sent = packets_sent + 1
                await asyncio.sleep(0.05) # 20 Hz
            else:
                ToSend:bytes = tools.pack_control_packet(0.0, 0.0, 0.0, 0.0) # pack all 0 inputs
                if ser != None:
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
        nonlocal pitch_angle
        nonlocal roll_angle
        nonlocal pitch_rate
        nonlocal roll_rate
        nonlocal yaw_rate

        # declare rxBuffer of all data received from transceiver through the USB serial line
        rxBuffer:bytearray = bytearray()

        # continuously monitor and receive new data from the serial port (from transceiver)
        while True:

            # read data if any is available!
            if ser != None:
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
                if ThisLine[0] & 0b00000001 == 0: # if bit 0 is 0, it is a telemetry packet
                    TelemetryData:dict = tools.unpack_telemetry(ThisLine)
                    if TelemetryData != None: # it returns None if there was an issue like it wasn't long enough
                        vbat = TelemetryData["vbat"]
                        pitch_rate = TelemetryData["pitch_rate"]
                        roll_rate = TelemetryData["roll_rate"]
                        yaw_rate = TelemetryData["yaw_rate"]
                        pitch_angle = TelemetryData["pitch_angle"]
                        roll_angle = TelemetryData["roll_angle"]
                elif ThisLine[0] & 0b00000001 > 0: # if bit 0 is 1, it is a special packet (text)
                    msg:str = tools.unpack_special_packet(ThisLine)
                    drone_messages.append(display.Message(msg, time.time()))
                else:
                    # handle uknown packet type?
                    pass
                
            # sleep
            await asyncio.sleep(0.05) # 20 Hz, faster than the 10 Hz the drone will send it at


    # we are all set and ready to go. Confirm.
    print()
    input("All set and ready to go! Enter to continue.")

    # get all threads going
    booted:float = time.time() # mark the boot time, in seconds. This will later be used to show system uptime
    task_read_xbox = asyncio.create_task(continuous_read_xbox())
    task_display = asyncio.create_task(continuous_display())
    task_radio_tx = asyncio.create_task(continuous_radio_tx())
    task_radio_rx = asyncio.create_task(continuous_radio_rx())
    await asyncio.gather(task_read_xbox, task_display, task_radio_tx, task_radio_rx) # infinitely wait for all to finish (which will never happen since they are infinitely running)


# run main program via asyncio
asyncio.run(main())