import machine
import time
import asyncio

def pack_status_packet_part1(m1_throttle:float, m2_throttle:float, m3_throttle:float, m4_throttle:float, pitch_rate:float, roll_rate:float, yaw_rate:float, pitch_angle:float, roll_angle:float) -> bytes:

    ToReturn:bytearray = bytearray()

    # Add header (metadata) byte
    header:int = 0b00000000 # bit 0 (right-most) is "0" to declare as status packet
    ToReturn.append(header)

    # all motor throttles are alraedy expressed as 0.0 to 1.0, a percentage
    # we will just get equivalent integer in 0-65535 scale by scaling
    # and then convert that int16 to 2 bytes

    # add M1 throttle
    asint16:int = min(max(int(m1_throttle * 65535), 0), 65535)
    ToReturn.extend(asint16.to_bytes(2, "big"))

    # add M2 throttle
    asint16:int = min(max(int(m2_throttle * 65535), 0), 65535)
    ToReturn.extend(asint16.to_bytes(2, "big"))

    # add M3 throttle
    asint16:int = min(max(int(m3_throttle * 65535), 0), 65535)
    ToReturn.extend(asint16.to_bytes(2, "big"))

    # add M4 throttle
    asint16:int = min(max(int(m4_throttle * 65535), 0), 65535)
    ToReturn.extend(asint16.to_bytes(2, "big"))

    # pitch rate, roll rate, and yaw rate will all be 
    # expressed as a percentage of the range from -180 d/s to 180 d/s
    # and then converted to an int16

    # add pitch rate
    aspop:float = (pitch_rate + 180) / 360
    asint16 = min(max(int(aspop * 65535), 0), 65535)
    ToReturn.extend(asint16.to_bytes(2, "big"))

    # add roll rate
    aspop:float = (roll_rate + 180) / 360
    asint16 = min(max(int(aspop * 65535), 0), 65535)
    ToReturn.extend(asint16.to_bytes(2, "big"))

    # add yaw rate
    aspop:float = (yaw_rate + 180) / 360
    asint16 = min(max(int(aspop * 65535), 0), 65535)
    ToReturn.extend(asint16.to_bytes(2, "big"))

    # pitch and roll angle will be expressed as a % of the range of -90 and 90
    # and then that % will then be scaled between 0-65535
    # and then that int16 number being converted to 2 bytes

    # add pitch angle
    aspop:float = (pitch_angle + 90) / 180
    asint16 = min(max(int(aspop * 65535), 0), 65535)
    ToReturn.extend(asint16.to_bytes(2, "big"))

    # add roll angle
    aspop:float = (roll_angle + 90) / 180
    asint16 = min(max(int(aspop * 65535), 0), 65535)
    ToReturn.extend(asint16.to_bytes(2, "big"))

    return bytes(ToReturn)

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
            data:bytes = pack_status_packet_part1(m1_throttle, m2_throttle, m3_throttle, m4_throttle, pitch_rate, roll_rate, yaw_rate, pitch_angle, roll_angle)

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