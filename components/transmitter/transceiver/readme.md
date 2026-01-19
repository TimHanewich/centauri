# Transceiver Platform
![transceiver](https://i.imgur.com/zod1oGl.png)

The transceiver platform is a USB‑connected support device that bridges the PC running the transmitter program with the quadcopter. Since the PC itself does not include an HC‑12 radio transceiver, this external module provides the necessary hardware to transmit and receive flight data. Communication flows through USB to the platform, which then interfaces with the HC‑12 for wireless exchange with the drone.

The platform is intentionally simple, consisting of three main components:
- **HC‑12 radio transceiver** - handles wireless communication, sending commands to the quadcopter and receiving telemetry back.  
- **Raspberry Pi Pico** - brokers data transfer between the PC and the HC‑12, while also providing lightweight meta‑telemetry to confirm the transceiver’s operational status.  
- **[CP2102 USB to UART module](https://a.co/d/4rJMLjy)** - connects directly to the PC via USB, enabling serial communication with the Raspberry Pi Pico.  

## 3D-Printed Base
To make assembly easier, I designed a compact 3D‑printed mount that secures the Raspberry Pi Pico and HC‑12 together. You can download the design below:
- [**V1** (uses the HC-12's spring antenna)](https://github.com/TimHanewich/centauri/releases/download/2/transceiver_platform.stl)
- **V2** (uses a separate 433 MHz antenna)
    - [Platform base](https://github.com/TimHanewich/centauri/releases/download/23/transceiver_plattform_v2.stl)
    - [Antenna base](https://github.com/TimHanewich/centauri/releases/download/23/antenna_base.stl)
    - You can also download the raw blender iterative files as I designed this [here](https://github.com/TimHanewich/centauri/releases/download/24/transceiver_platform_v2.zip).

Once the platform is assembled, flash the required firmware files from [./src/transceiver/](./src/transceiver/) onto the Pico to complete setup.