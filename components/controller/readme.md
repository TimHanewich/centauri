# The Pilot's Controller
![controller](https://i.imgur.com/KFdf4A0.png)

Flying the Centauri quadcopter requires a dedicated control interface - and just like the frame itself, the controller system is fully custom‑built. It combines familiar hardware with bespoke software and radio communication to deliver real‑time responsiveness.

The controller is composed of three key components working together to transmit and receive flight data:
- **Xbox Controller**: An Xbox Series X/S controller (connected via USB to a PC) provides the pilot's input.  
  - Throttle → Right Trigger  
  - Pitch & Roll → Left Stick  
  - Yaw → Right Stick (X axis)  
- **Python Program**: Running on the PC, this program reads the controller inputs, converts them into structured data packets, and transmits them to the quadcopter. It also performs additional tasks, which are explained in later sections.  
- **Transceiver Platform**: A USB‑connected microcontroller paired with an HC‑12 radio module acts as the communication bridge between the PC and the quadcopter, enabling bidirectional data exchange over wireless signals.  

## Controller Program Described
The controller program, [main.py](./src/PC/main.py) is primarily responsible for handling communication between the pilot (who is inputting control commands via the Xbox controller) and the quadcopter.

The program runs an infinite loop with the following steps summarized below:
1. Reads control input from the Xbox controller
2. Packs that input into a special encoded, dense data packet structure
3. Sends that data packet to the attached transceiver via serial USB connection (the transceiver, in turn, transmits it to the quadcopter)

But that isn't all the control program does - the control program also listens to telemetry being broadcasted *back* from the drone to the pilot (i.e. battery level, rates, error messages, etc) and can also flash new PID settings over to the quadcopter to update flight settings on the fly!

The control program uses the [pygame](https://pypi.org/project/pygame/) package for reading input from the Xbox controller, the [rich](https://pypi.org/project/rich/) library for rendering a "live display" of telemetry during operation, the [pyserial](https://pypi.org/project/pyserial/) library for serial communication with the USB-connected transceiver, and the [keyboard](https://pypi.org/project/keyboard/) package for recognizing keyboard inputs from the pilot to do things like change settings.

## Transceiver Platform