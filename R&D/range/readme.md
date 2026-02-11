## Possible Causes of Range Issues
- Fresnel zone interferance (transmitter/drone is too low to ground)
- No ground planes used
- Are the HC-12's clones?
- Drone side
    - LiPo battery blocking LoS
    - LiPo battery proximity to antenna
    - The [antennas proximity to the battery's wire leads](https://i.imgur.com/1P4goUB.jpeg) is causing interferance
    - The HC-12 it getting a 5v supply with interferance from the ESCs (dirty) - maybe a capacitor would help? (perhaps this is unlikely as it isn't *sending* while flying, only passively *receiving*, which takes barely any current I think)
- Transmitter side
    - Tx HC-12 has weakened
    - Tx HC-12 not configured to transmit at full power? (my fault not configuring it correctly?)
    - Power Supply issues
        - [CP2102 USB to UART module](https://a.co/d/4rJMLjy) is not supplying it with enough current to transmit at full power 
        - the laptop's USB port is not supplying enough current at all (not 500 mA expected)
        - The energy supply the laptop is supplying has interferance in it
    - The ufl to SMA connector I am using to connect the antenna to the HC-12 is cheap and "leaking" energy
    - The proximity of it to the laptop is causing interferance

## Prompt
```
Consider the following scenario:

Two HC-12s are used. One as a transmitter, one as a receiver.
The transmitter is using a 433 MHz antenna with ~1.5 SWR
The receiver is using a 433 MHz antenna with ~1.1 SWR
The transmitter is resting on a picnic table, plugged in via USB to a laptop
The receiver is mounted at the rear on a quadcopter drone, 3-4 centimeters away from the 4S LiPo battery
Both use a baudate of 9600, FU3 mode, and the transmitting HC-12 is transmitting at full power
It is a completely open field with good line of sight.
The Rx antenna has line of sight to the Tx antenna
No intentional ground planes are used


```