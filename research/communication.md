# Centauri Communication Protocol
Two HC-12 radio transceiver modules will be used to facilitate bidirectional remote communications between the remote controller and the drone. Serial UART will be used to facillitate bidirectional communication between the HL MCU and LL MCU.

Communication Timing:
- PC sends control packets to transceiver at 50 Hz
- Transceiver checks for new control packets at 100 Hz and sends via HC-12 right away (effective 50 Hz)
- HL MCU checks for new packets received via HC-12 at 100 Hz
- HL MCU provides control packets to LL MCU when they are receive (effective 50 Hz)
- LL MCU provides status updates to HL MCU at 10 Hz
- HL MCU sends status updates to remote controller via HC-12 at 10 Hz

## Controller --> Quadcopter Communication
Of the data packets that are sent from the remote controller --> quadcopter, there are 2 bits used for 4 separate packet types:
- `00` = config packet
- `01` = control packet

### Config Packet
Remote controller --> HL MCU via HC-12, HL MCU --> LL MCU via UART.

Used to update settings on the LL MCU on the go without having to manually re-flash code. **Note that the LL MCU will NOT save these to hard storarage and "memorize" these when re-booted. So, this shoud be sent at every boot.**

- Metadata byte (1 byte)
    - Bit 7: *reserved*
    - Bit 6: *reserved*
    - Bit 5: *reserved*
    - Bit 4: *reserved*
    - Bit 3: *reserved*
    - Bit 2: *reserved*
    - Bit 0 and 1: pack identifier
        - Bit 1: `0`
        - Bit 0: `0`
- PID Settings: Used by LL MCU
    - Roll_P (4 bytes): roll P value
    - Roll_I (4 bytes): roll I value
    - Roll_D (4 bytes): roll D value
    - Pitch_P (4 bytes): pitch P value
    - Pitch_I (4 bytes): pitch I value
    - Pitch_D (4 bytes): pitch D value
    - Yaw_P (4 bytes): yaw P value
    - Yaw_I (4 bytes): yaw I value
    - Yaw_D (4 bytes): yaw D value
    - I_Limit (4 bytes): max I-term limit (from PID equation) to prevent over-spooling, applied to Roll, Pitch, and Yaw PIDs
- Rate mode settings: used by LL MCU
    - Max_Roll_Rate (4 bytes): max roll rate (degrees per second), in either direction
    - Max_Pitch_Rate (4 bytes): max pitch rate (degrees per second) in either direction
    - Max_Yaw_Rate (4 bytes): max yaw rate (degrees per second) in either direction
- Angle mode settings: used by HL MCU
    - Max_Pitch_Angle (4 bytes): max pitch angle in either direction, left or right
    - Max_Roll_Angle (4 bytes): max roll angle in either direction, left or right
- "\r\n" (2 bytes): endline to mark the end of the packet

### Control Packet
Remote controller --> HL MCU via HC-12, HL MCU --> LL MCU via UART.

This data packet contains all necessary data for controlling normal flight characteristics of the drone.

- Metadata byte (1 byte)
    - Bit 7: *reserved*
    - Bit 6: *reserved*
    - Bit 5: *reserved*
    - Bit 4: *reserved*
    - Bit 3: **control mode**. 0 = rate mode, 1 = attitude (angle) mode
    - Bit 2: **arm**. 0 = unarmed, idle on ground, motors arrested. 1 = armed, motors at least idling at min throttle but no lift.
    - Bit 1 and 0: **pack identifier**
        - Bit 1 = `0`
        - Bit 0 = `1`
- Throttle (2 bytes)
- Roll input (2 bytes): roll stick input, can be used to calculate desired roll rate or angle
- Pitch input (2 bytes): pitch stick input, can be used to calculate desired pitch rate or angle
- Yaw input (2 bytes): yaw input, can be used to calculate desired yaw rate
- **Checksum** (1 byte): XOR chain based on all the above bytes
- "\r\n" end line (2 bytes)

## Quadcopter --> Remote Controller
Of the data packets that are sent from quadcopter --> controller, there is 1 bit used for 2 separate packet types:
- `0` = status packet
- `1` = special packet (free-form text)

### Status Packet
LL MCU --> HL MCU via UART, HL MCU --> Remote Controller via HC-12.

- Metadata byte (1 byte)
    - Bit 7: *reserved*
    - Bit 6: *reserved*
    - Bit 5: *reserved*
    - Bit 4: *reserved*
    - Bit 3: *reserved*
    - Bit 2: *reserved*
    - Bit 1: *reserved*
    - Bit 0: packet identifier (set to `0` to declare as status packet)
- M1 throttle (2 bytes)
- M2 throttle (2 bytes)
- M3 throttle (2 bytes)
- M4 throttle (2 bytes)
- Actual Roll Rate, in degrees per second (2 bytes)
- Actual Pitch Rate, in degrees per second (2 bytes)
- Actual Yaw Rate, in degrees per second (2 bytes)
- Roll Angle Estimate (2 bytes): from complementary filter performed on LL MCU
- Pitch Angle Estimate (2 bytes): from complementary filter performed on LL MCU
- *HL MCU will append before sending to remote controller via HC-12...*
    - Battery level as voltage (2 bytes):
    - TF Luna Reading: Distance (2 bytes)
    - TF Luna Reading: Strength (2 bytes)
    - BMP180 Reading: altitude (2 bytes)
    - QMC5883L reading (1 byte)
- "\r\n" end line (2 bytes)

### Special Packet (free text)
Drone --> HC-12 --> HC-12 --> Transceiver --> PC

- Metadata byte (1 byte)
    - Bit 7: *reserved*
    - Bit 6: *reserved*
    - Bit 5: *reserved*
    - Bit 4: *reserved*
    - Bit 3: *reserved*
    - Bit 2: *reserved*
    - Bit 1: *reserved*
    - Bit 0: packet identifier (set to `1` to declare as special packet)
- Message bytes (plain text encoded as ASCII) - *any number of bytes*
- "\r\n" end line (2 bytes)

## HL MCU --> LL MCU Confirmation of Life
The HL MCU may send the following over UART to the LL MCU to confirm it is on and okay:

```
TIMHPING\r\n
```

The "TIMH" (84, 73, 77, 72) beginning 4 bytes mark the line as an "internal message". **Not** a message from the controller, but rather a message from the HL MCU to confirm the LL MCU is working.

If the LL MCU receives this, it should respond with the following:

```
TIMHPONG\r\n
```

Again, the preceeding "TIMH" marks the message as one that originates from the LL MCU, explicitly for the HL MCU, **not** something to be passed along to the controller.