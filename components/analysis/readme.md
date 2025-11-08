# Analysis Script
The Centauri quadcopter will log telemetry onboard the Raspberry Pi Pico's flash storage. You can plug the Pico of the quadcopter into a computer and extract the telemetry file (`log` on the root directory). However, this file is a binary data file that has binary compact packets of telemetry stored in it. To make any sense of it, you will need a separate script that unpacks this data into a human-readable format like a `.csv` file.

[This simple analysis script](./src/main.py) allows you to do that. When you run it, it will prompt you to give two inputs: the location, on your computer (path), or where the binary file exists, and then the target location of the `.csv` file output. Once you give it both, you'll see it unpack the data.

Below is some sample telemetry:

![telemetry](https://i.imgur.com/522dEtC.png)

As seen above, the telemetry logged maps several onboard parameter values against a timestamp:
- **Battery Voltage** - the supply voltage by the onboard battery.
- **Pitch Rate** - the *actual* pitch rate, in degrees per second.
- **Roll Rate** - the *actual* roll rate, in degrees per second.
- **Yaw Rate** - the *actual* yaw rate, in degrees per second.
- **Input Throttle** - the input throttle percentage from the pilot in that moment, expressed in terms of a percentage from 0 to 100.
- **Input Pitch** - the actual pitch input percentage from the pilot, expressed in terms of a percentage from -100 to 100.
- **Input Roll** - the actual roll input percentage from the pilot, expressed in terms of a percentage from -100 to 100.
- **Input Yaw** - the actual yaw input percentage from the pilot, expressed in terms of a percentage from -100 to 100.
- **M1 Throttle** - front left motor throttle in that moment (determined by the flight controller to comply with the pilot's desired input)
- **M2 Throttle** - front right motor throttle in that moment (determined by the flight controller to comply with the pilot's desired input)
- **M3 Throttle** - rear left motor throttle in that moment (determined by the flight controller to comply with the pilot's desired input)
- **M4 Throttle** - rear right motor throttle in that moment (determined by the flight controller to comply with the pilot's desired input)