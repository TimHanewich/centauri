# Centauri Communication Protocol
Two HC-12 radio transceiver modules will be used to facilitate bidirectional remote communications between the remote controller and the drone. Serial UART will be used to facillitate bidirectional communication between the HL MCU and LL MCU.

**PC --> Transceiver --> HL-MCU --> LL-MCU**

## Communication Timing

## Communication Between PC and Tranceiver
If the communication between the PC and Transceiver begins with "TIMH", that means it is an "internal message", intended to only be shared between them. If it does not begin with that, it is merely intended to "pass through" the transceiver to the drone or PC.

- PC --> Transceiver
    - **For Transceiver**: PING (request for confirmation of life): `TIMHPING\r\n`
    - **For Drone**: Raw bytes data (*transceiver does not need to unpack it, just pass it along*)
- Transceiver --> PC
    - **From Transceiver**: PONG (confirmation of life) : `TIMHPONG\r\n`
    - **From Transceiver**: Special Packet (text) - *i.e. errors, problems*
    - **Passed along from drone**: Raw bytes data (*transceiver does not need to unpack it, just pass it along*)

## Communication Between Transceiver and HL-MCU (via HC-12)
- Transceiver --> HL-MCU
    - Control Settings Update
        - Metadata byte:
            - Bit 7: *reserved*
            - Bit 6: *reserved*
            - Bit 5: *reserved*
            - Bit 4: *reserved*
            - Bit 3: *reserved*
            - Bit 2: *reserved*
            - Bit 1: `0` (packet identifier)
            - Bit 0: `0` (packet identifier)
        - Idle Throttle: 2 bytes
        - Max Throttle: 2 bytes
        - Max Pitch Rate (Rate Mode): 2 bytes
        - Max Roll Rate (Rate Mode): 2 bytes
        - Max Yaw Rate (Rate Mode): 2 bytes
        - Max Pitch Angle (Angle Mode): 2 bytes
        - Max Roll angle (Angle Mode): 2 bytes
    - PID Settings Update
        - Metadata byte:
            - Bit 7: *reserved*
            - Bit 6: *reserved*
            - Bit 5: *reserved*
            - Bit 4: *reserved*
            - Bit 3: *reserved*
            - Bit 2: *reserved*
            - Bit 1: `0` (packet identifier)
            - Bit 0: `1` (packet identifier)
        - Pitch P Gain
        - Pitch I Gain
        - Pitch D Gain
        - Roll P Gain
        - Roll I Gain
        - Roll D Gain
        - Yaw P Gain
        - Yaw I Gain
        - Yaw D Gain
        - PID I Limit
    - Control Packet
        - Metadata byte:
            - Bit 7: *reserved*
            - Bit 6: *reserved*
            - Bit 5: *reserved*
            - Bit 4: *reserved*
            - Bit 3: **control mode**. 0 = rate mode, 1 = angle mode
            - Bit 2: **armed**. 0 = unarmed, idle on ground. 1 = armed, motors spin at idle speed.
            - Bit 1: `1` (packet identifier)
            - Bit 0: `0` (packet identifier)
        - Throttle (2 bytes)
        - Pitch (2 bytes)
        - Roll (2 bytes)
        - Yaw (2 bytes)
- HL-MCU --> Transceiver
    - Control Status
    - System Status
    - Special Packet (text) 
    
## Communication Between HL-MCU and LL-MCU
If the communication between the HL-MCU and LL-MCU begins with "TIMH", that means it is an "internal message", intended to only be shared between them. If it does not begin with that, it is merely intended to "pass through" to the remote controller.
- HL-MCU --> LL-MCU:
    - PING (request for confirmation of life): `TIMHPING\r\n`
    - Settings Update
        - Header byte (metadata)
            - Bit 7: *reserved*
            - Bit 6: *reserved*
            - Bit 5: *reserved*
            - Bit 4: *reserved*
            - Bit 3: *reserved*
            - Bit 2: *re served*
            - Bit 1: *reserved*
            - Bit 0: `0` = packet identifier
        - Pitch P Gain (4 bytes)
        - Pitch I Gain (4 bytes)
        - Pitch D Gain (4 bytes)
        - Roll P Gain (4 bytes)
        - Roll I Gain (4 bytes)
        - Roll D Gain (4 bytes)
        - Yaw P Gain (4 bytes)
        - Yaw I Gain (4 bytes)
        - Yaw D Gain (4 bytes)
        - I Limit (4 bytes)
        - XOR-chain based checksum (1 byte)
    - Desired Rates
        - Header byte (metadata)
            - Bit 7: *reserved*
            - Bit 6: *reserved*
            - Bit 5: *reserved*
            - Bit 4: *reserved*
            - Bit 3: *reserved*
            - Bit 2: *re served*
            - Bit 1: *reserved*
            - Bit 0: `1` = packet identifier
        - Throttle (2 bytes)
        - Desired Pitch Rate (4 bytes)
        - Desired Roll Rate (4 bytes)
        - Desired Yaw Rate (4 bytes)
        - XOR-chain based checksum (1 byte)
- LL-MCU --> HL-MCU:
    - PONG (confirmation of life): `TIMHPING\r\n`
    - Status
        - Header byte (metadata)
        - Bit 7: *reserved*
            - Bit 6: *reserved*
            - Bit 5: *reserved*
            - Bit 4: *reserved*
            - Bit 3: *reserved*
            - Bit 2: *re served*
            - Bit 1: *reserved*
            - Bit 0: `0` = packet identifier
        - M1 throttle (1 byte)
        - M2 throttle (1 byte)
        - M3 throttle (1 byte)
        - M4 throttle (1 byte)
        - Actual Pitch Rate (4 bytes)
        - Actual Roll Rate (4 bytes)
        - Actual Yaw Rate (4 bytes)
        - Estimated Pitch Angle (4 bytes)
        - Estimated Roll Angle (4 bytes)