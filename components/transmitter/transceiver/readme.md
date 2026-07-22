# Transceiver Platform
![transceiver](https://i.imgur.com/AWLlA8g.jpeg)

The transceiver platform is a USB‑connected support device that bridges the PC running the transmitter program with the quadcopter. Since the PC itself does not include an HC‑12 radio transceiver, this external module provides the necessary hardware to transmit and receive flight data. Communication flows through USB to the platform, which then interfaces with the HC‑12 for wireless exchange with the drone.

The platform is intentionally simple, consisting of three main components:
- **HC‑12 radio transceiver** - handles wireless communication, sending commands to the quadcopter and receiving telemetry back.  
- **Raspberry Pi Pico** - brokers data transfer between the PC and the HC‑12, while also providing lightweight meta‑telemetry to confirm the transceiver’s operational status.  
- **[CP2102 USB to UART module](https://a.co/d/4rJMLjy)** - connects directly to the PC via USB, enabling serial communication with the Raspberry Pi Pico.  

## 3D-Printed Base
I designed a compact 3D‑printed mount that secures the Raspberry Pi Pico and HC‑12 together, along with a base that allows the antenna to be screwed in. You can download the design [from Thingiverse](https://www.thingiverse.com/thing:7386349).

The raw blender iterative files as I designed this can be downloaded [here](https://github.com/TimHanewich/centauri/releases/download/24/transceiver_platform_v2.zip)

Once the platform is assembled, flash the required firmware files from [./src/](./src/) onto the Pico to complete setup.

### Archived Designs
- [**V1** (uses the HC-12's spring antenna)](https://github.com/TimHanewich/centauri/releases/download/2/transceiver_platform.stl)