import machine
import time
import asyncio

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

    # Run all threads!
    task_comms_rx = asyncio.create_task(comms_rx())
    await asyncio.gather(task_comms_rx)

asyncio.run(main())