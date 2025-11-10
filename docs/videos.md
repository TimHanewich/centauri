# Video Series


- **Chapter 1**: Introduction
    - The components
    - How the data flows
- Then dive into each component more:
    - **Chapter 2: The Controller**
        - Uses pygame to get xbox controller input
        - Uses rich to show the display
        - Uses async to do everything at once
        - Reads input from pygame, min/maxs it with the min/max throttle
        - Uses tools.py to pack into a data packet
        - Uses pyserial to send data to transceiver platform, which then sends it to the quadcopter
        - The pyserial program passes along everything except TIMHPONG.
        - The transceiver also receives data coming in from quadcopter. Telemetry data.
        - Telemetry data shown in the pilot control.
        - Not just used for control input. Also used for settings flashing!
    - **Chapter 3: The Quadcopter**
    - **Chapter 4: The Analysis Script**