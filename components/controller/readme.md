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

## Controller Program
The controller software, [main.py](./src/PC/main.py), serves as the communication hub between the pilot and the quadcopter. It continuously processes inputs from the Xbox controller, encodes them into compact data packets, and relays them to the drone via the transceiver.

At its core, the program runs an infinite loop with three main steps:
1. **Read inputs** from the Xbox controller  
2. **Encode inputs** into a dense, structured data packet  
3. **Transmit packets** to the USB‑connected transceiver, which forwards them wirelessly to the quadcopter  

Beyond sending commands, the program also **receives telemetry** broadcasted back from the drone, such as battery status, flight rates, and error messages, and can **update PID settings on the fly**, allowing real‑time tuning of flight performance.

Key libraries used:
- **[pygame](https://pypi.org/project/pygame/)** — captures Xbox controller input  
- **[rich](https://pypi.org/project/rich/)** — renders a live telemetry dashboard during operation  
- **[pyserial](https://pypi.org/project/pyserial/)** — manages serial communication with the transceiver  
- **[keyboard](https://pypi.org/project/keyboard/)** — detects pilot keyboard commands for adjusting settings  

## Transceiver Platform