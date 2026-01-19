# The Pilot's Transmitter
![transmitter](https://i.imgur.com/6v91FmT.jpeg)

Flying the Centauri quadcopter requires a dedicated control interface - and just like the frame itself, the controller system is fully custom‑built. It combines familiar hardware with bespoke software and radio communication to deliver real‑time responsiveness.

The all-up transmitter is composed of three key components working together to transmit and receive flight data:
- **Xbox Controller**: An Xbox Series X/S controller (connected via USB to a PC) provides the pilot's input.  
  - Throttle → Right Trigger  
  - Pitch & Roll → Left Stick  
  - Yaw → Right Stick (X axis)  
- [**Python Program**](./PC/): Running on the PC, this program reads the controller inputs, converts them into structured data packets, and transmits them to the quadcopter. It also performs additional tasks, which are explained in later sections.  
- [**Transceiver Platform**](./transceiver/): A USB‑connected microcontroller paired with an HC‑12 radio module acts as the communication bridge between the PC and the quadcopter, enabling bidirectional data exchange over wireless signals.  

All three components are depicted below:

![controller](https://i.imgur.com/KFdf4A0.png)

