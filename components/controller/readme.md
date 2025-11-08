# The Pilot's Controller
![controller](https://i.imgur.com/KFdf4A0.png)

To fly a quadcopter, a pilot needs a controller interface! Like the Centauri quadcopter design, this controller system is also fully custom developed.

The controller consists of three components that work together to transmit control updates to the quadcopter in realtime:
- **An Xbox Controller** (Xbox Series X/S controller in my case) is connected to a PC via USB. The pilot uses this to input control commands
    - Throttle = Right Trigger
    - Pitch & Roll = Left Stick
    - Yaw = Right Stick's X axis
- **A Python Program** runs on the PC and collects input data from the Xbox controller, transforms this to data packets, and then sends these to the quadcopter. The program also does more than that, further explained in the sections below.
- **Transceiver Platform** - a USB-connected microcontroller and HC-12 pair are connected to the PC via USB and serve as the broker between the quadcopter and the PC, allowing for the bidirectional exchange of data over radio comnmunications.