# Transmitter Program
The transmitter software, [main.py](./src/PC/main.py), serves as the communication hub between the pilot and the quadcopter. It continuously processes inputs from the Xbox controller, encodes them into compact data packets, and relays them to the drone via the transceiver.

At its core, the program runs an infinite loop with three main steps:
1. **Read inputs** from the Xbox controller  
2. **Encode inputs** into a dense, structured data packet  
3. **Transmit packets** to the USB‑connected transceiver, which forwards them wirelessly to the quadcopter  

Beyond sending commands, the program also **receives telemetry** broadcasted back from the drone, such as battery status, flight rates, and error messages, and can **update PID settings on the fly**, allowing real‑time tuning of flight performance.

Key libraries used:
- **[pygame](https://pypi.org/project/pygame/)** - captures Xbox controller input  
- **[rich](https://pypi.org/project/rich/)** - renders a live telemetry dashboard during operation  
- **[pyserial](https://pypi.org/project/pyserial/)** - manages serial communication with the transceiver  
- **[keyboard](https://pypi.org/project/keyboard/)** - detects pilot keyboard commands for adjusting settings  