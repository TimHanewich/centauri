## Possible Causes of Range Issues
- Fresnel zone interferance (transmitter/drone is too low to ground)
- No ground planes used
- Are the HC-12's clones?
- Drone side
    - **ESCs contaminating the HC-12's power supply** <-- *quite sure this is it!*
    - LiPo battery blocking LoS
    - LiPo battery proximity to antenna (2-4 cm away)
    - The [battery's wires touching the antenna](https://i.imgur.com/1P4goUB.jpeg) could be causing interferance
    - The HC-12 it getting a 5v supply with interferance from the ESCs (dirty) - maybe a capacitor would help? (perhaps this is unlikely as it isn't *sending* while flying, only passively *receiving*, which takes barely any current I think)
- Transmitter side
    - Tx HC-12 has weakened (*can I use the RTL-SDR to compare Tx power to a new HC-12?*)
    - Tx HC-12 not configured to transmit at full power? (my fault not configuring it correctly?)
    - Power Supply issues
        - [CP2102 USB to UART module](https://a.co/d/4rJMLjy) is not supplying it with enough current to transmit at full power 
        - the laptop's USB port is not supplying enough current at all (not 500 mA expected)
        - The energy supply the laptop is supplying has interferance in it
    - The ufl to SMA connector I am using to connect the antenna to the HC-12 is cheap and "leaking" energy
    - The proximity of it to the laptop is causing interferance

## Files
- [Fresnel Zone Calculator `.xlsx`](https://github.com/TimHanewich/centauri/releases/download/43/fresnel_calculator.xlsx)