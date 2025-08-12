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
    - Settings Update
    - Control Packet
- HL-MCU --> Transceiver
    - Status Packet
    - Special Packet (text) 
    
## Communication Between HL-MCU and LL-MCU
If the communication between the HL-MCU and LL-MCU begins with "TIMH", that means it is an "internal message", intended to only be shared between them. If it does not begin with that, it is merely intended to "pass through" to the remote controller.
- HL-MCU --> LL-MCU:
    - PING (request for confirmation of life): `TIMHPING\r\n`
    - Settings Update
    - Desired Rates (normal control)
- LL-MCU --> HL-MCU:
    - PONG (confirmation of life): `TIMHPING\r\n`
    - Status Packet
    