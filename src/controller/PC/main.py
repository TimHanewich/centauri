import pygame
import time
import display
import asyncio
import rich.table
import rich.console
import rich.live

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

    # set up control inputs
    armed:bool = False
    mode:bool = False
    throttle:float = 0.0 # 0.0 to 1.0
    pitch:float = 0.0
    roll:float = 0.0
    yaw:float = 0.0

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
                
                # get table
                tbl = display.construct(dp)

                # update live
                l.update(tbl)

                # wait
                await asyncio.sleep(0.01)

    # we are all set and ready to go. Confirm.
    print()
    input("All set and ready to go! Enter to continue.")

    # get all threads going
    task_read_xbox = asyncio.create_task(continuous_read_xbox())
    task_display = asyncio.create_task(continuous_display())
    await asyncio.gather(task_read_xbox, task_display) # infinitely wait for all to finish (which will never happen since they are infinitely running)


# run main program via asyncio
asyncio.run(main())