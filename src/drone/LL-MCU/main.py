import machine
import time
import asyncio
import tools

async def main() -> None:

    # First thing is first: set up onboard LED, turn it on while loading
    led = machine.Pin("LED", machine.Pin.OUT)
    led.on()

    # establish failure pattern
    def FATAL_ERROR() -> None:
        while True:
            led.on()
            time.sleep(1.0)
            led.off()
            time.sleep(1.0)

    # set up UART interface with HL MCU
    uart = machine.UART(0, tx=machine.Pin(12), rx=machine.Pin(13), baudrate=115200)

    # declare variables that will be used throughout
    m1_throttle:float = 0.0
    m2_throttle:float = 0.0
    m3_throttle:float = 0.0
    m4_throttle:float = 0.0
    pitch_rate:float = 0.0
    roll_rate:float = 0.0
    yaw_rate:float = 0.0
    pitch_angle:float = 0.0
    roll_angle:float = 0.0

    async def ledflicker() -> None:
        """Continuously flick the onboard LED."""
        nonlocal led
        while True:
            led.on()
            await asyncio.sleep(0.25)
            led.off()
            await asyncio.sleep(0.25)

    async def comms_rx() -> None:
        """Handles receiving of any data from the HL MCU"""

        # declare nonlocal variables
        nonlocal uart

        while True:
            if uart.any() > 0:
                data:bytes = uart.readline()

                # handle according to what it is
                if data == "TIMHPING\r\n".encode(): # simple check of life
                    uart.write("TIMHPONG\r\n".encode()) # respond pong
                else:
                    print("Unknown data received: " + str(data))
            
            # wait
            await asyncio.sleep(0.01) # 100 Hz max

    async def comms_tx() -> None:
        """Handles continuous sending of status data to HL MCU."""

        # declare nonlocal variables
        nonlocal uart
        nonlocal m1_throttle
        nonlocal m2_throttle
        nonlocal m3_throttle
        nonlocal m4_throttle
        nonlocal pitch_rate
        nonlocal roll_rate
        nonlocal yaw_rate
        nonlocal pitch_angle
        nonlocal roll_angle

        while True:

            # pack all data
            data:bytes = tools.pack_status_packet_part1(m1_throttle, m2_throttle, m3_throttle, m4_throttle, pitch_rate, roll_rate, yaw_rate, pitch_angle, roll_angle)

            # send the data
            uart.write(data + "\r\n".encode())

            # wait
            await asyncio.sleep(0.1) # 10 Hz

    # Run all threads!
    task_led_flicker = asyncio.create_task(ledflicker())
    task_comms_rx = asyncio.create_task(comms_rx())
    task_comms_tx = asyncio.create_task(comms_tx())
    await asyncio.gather(task_led_flicker, task_comms_rx, task_comms_tx)

asyncio.run(main())