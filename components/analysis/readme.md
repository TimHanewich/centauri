# Analysis Script

The Centauri quadcopter logs telemetry directly onto the Raspberry Pi Pico’s onboard flash storage. After a flight, you can connect the Pico to a computer and extract the telemetry file (`log` in the root directory). This file is stored in a compact binary format, with densely encoded telemetry packets. To interpret the data, you’ll need a separate script that unpacks it into a human‑readable format such as a `.csv`.

[This analysis script](./src/main.py) performs that conversion. When executed, it prompts for two inputs:
1. The path to the binary telemetry file on your computer  
2. The target path for the `.csv` output  

As you can see below, the Centauri quadcopter will log telemetry as a binary file named `log`. That data can be retrieved from the microcontroller via Thonny.

![log](https://i.imgur.com/B5EOT7c.png)

Use can use this analysis script to decode the binary `log` file and generate a structured `.csv` file for easy inspection. Below is an example of the telemetry output:

![telemetry](https://i.imgur.com/522dEtC.png)

As shown above, the telemetry maps multiple onboard parameters against a timestamp, including:

- **Battery Voltage** - supply voltage from the onboard battery  
- **Pitch Rate** - actual pitch rate (°/s)  
- **Roll Rate** - actual roll rate (°/s)  
- **Yaw Rate** - actual yaw rate (°/s)  
- **Input Throttle** - pilot throttle input, expressed as a percentage (0–100)  
- **Input Pitch** - pilot pitch input, expressed as a percentage (−100 to 100)  
- **Input Roll** - pilot roll input, expressed as a percentage (−100 to 100)  
- **Input Yaw** - pilot yaw input, expressed as a percentage (−100 to 100)  
- **M1 Throttle** - front‑left motor throttle (calculated by the flight controller)  
- **M2 Throttle** - front‑right motor throttle (calculated by the flight controller)  
- **M3 Throttle** - rear‑left motor throttle (calculated by the flight controller)  
- **M4 Throttle** - rear‑right motor throttle (calculated by the flight controller)  
