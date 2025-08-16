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
        - Max Pitch Rate, in degrees per second (Rate Mode): 1 byte (*this is interpretted literally... i.e. a value of 30 would be 30 degrees/second*)
        - Max Roll Rate, in degrees per second (Rate Mode): 1 byte (*this is interpretted literally... i.e. a value of 30 would be 30 degrees/second*)
        - Max Yaw Rate, in degrees per second (Rate Mode): 1 byte (*this is interpretted literally... i.e. a value of 30 would be 30 degrees/second*)
        - Max Pitch Angle (Angle Mode): 1 byte (*this is interpretted literally... i.e. a value of 30 would be 30 degrees*)
        - Max Roll angle (Angle Mode): 1 byte (*this is interpretted literally... i.e. a value of 30 would be 30 degrees*)
        - XOR-chain based checksum
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
        - Throttle input % (2 bytes, uint16)
        - Pitch input % (2 bytes, int16)
        - Roll input % (2 bytes, int16)
        - Yaw input % (2 bytes, int16)
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
            - Bit 2: *reserved*
            - Bit 1: *reserved*
            - Bit 0: `0` = packet identifier
        - Pitch P Gain (2 bytes, uint16)
        - Pitch I Gain (2 bytes, uint16)
        - Pitch D Gain (2 bytes, uint16)
        - Roll P Gain (2 bytes, uint16)
        - Roll I Gain (2 bytes, uint16)
        - Roll D Gain (2 bytes, uint16)
        - Yaw P Gain (2 bytes, uint16)
        - Yaw I Gain (2 bytes, uint16)
        - Yaw D Gain (2 bytes, uint16)
        - I Limit (2 bytes, uint16)
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
        - Throttle (2 bytes, uint16)
        - Desired Pitch Rate (2 bytes, int16)
        - Desired Roll Rate (2 bytes, int16)
        - Desired Yaw Rate (2 bytes, int16)
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
        - Actual Pitch Rate: 1 signed byte, interpretted literally
        - Actual Roll Rate: 1 signed byte, interpretted literally
        - Actual Yaw Rate: 1 signed byte, interpretted literally
        - Estimated Pitch Angle: 1 signed byte, interpretted literally
        - Estimated Roll Angle: 1 signed byte, interpretted literally