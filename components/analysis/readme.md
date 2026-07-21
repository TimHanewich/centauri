# Telemetry Extraction & Analysis
The Centauri quadcopter logs telemetry directly onto the Raspberry Pi Pico's onboard flash storage, several times per second. After a flight, you can connect the Pico to a computer and extract the telemetry file (`log` in the root directory). This file is stored in a compact binary format, with densely encoded telemetry packets. To interpret the data, you'll need a separate script that unpacks it into a human‑readable format such as a `.csv`.

[This analysis script](./src/main.py) performs that conversion. When run, it:
1. Prompts for the path to the binary `log` file on your computer, then unpacks all the telemetry frames within it.
2. Infers each individual "flight" in the log (a span of time when the quadcopter went from unarmed --> armed --> unarmed again) and prints summary stats for each: duration, battery voltage range, G-force range, average throttle, and Rx (command receipt) latency.
3. Prompts for a target path to save the unpacked telemetry to as a `.csv` file.

As you can see below, the Centauri quadcopter will log telemetry as a binary file named `log`. That data can be retrieved from the microcontroller via Thonny.

![log](https://i.imgur.com/B5EOT7c.png)

Use can use this analysis script to decode the binary `log` file and generate a structured `.csv` file for easy inspection. Below is an example of the telemetry output:

![telemetry](https://i.imgur.com/522dEtC.png)

As shown above, the telemetry maps multiple onboard parameters against a timestamp, including:

- **Seconds** - the exact timestamp, in seconds, this telemetry frame was taken at (note this may *decrease* if the quadcopter is rebooted, resetting system time back to 0)
- **Battery Voltage** - supply voltage from the onboard battery  
- **Pitch Rate** - actual pitch rate (°/s)  
- **Roll Rate** - actual roll rate (°/s)  
- **Yaw Rate** - actual yaw rate (°/s)  
- **Pitch Angle** and **Roll Angle** - angle estimates calculated by the flight controller's complementary filter
- **G-Force** - how many G's the quadcopter is pulling at that moment
- **Input Throttle** - pilot throttle input, expressed as a percentage (0–100)  
- **Input Pitch** - pilot pitch input, expressed as a percentage (−100 to 100)  
- **Input Roll** - pilot roll input, expressed as a percentage (−100 to 100)  
- **Input Yaw** - pilot yaw input, expressed as a percentage (−100 to 100)  
- **M1 Throttle** - front‑left motor throttle (calculated by the flight controller)  
- **M2 Throttle** - front‑right motor throttle (calculated by the flight controller)  
- **M3 Throttle** - rear‑left motor throttle (calculated by the flight controller)  
- **M4 Throttle** - rear‑right motor throttle (calculated by the flight controller)  
- **Cmd Last Received ms** - how long ago (in milliseconds) a Control Packet was last received from the transmitter, helping indicate Rx issues

## Try it yourself!
You can try converting and analyzing *Centauri* telemetry with nothing more than a computer that has Python installed. Below are a few direct download links to raw `log` binary files to experiment with:
- [February 13, 2026: Corrupt Packet Failure](https://github.com/TimHanewich/centauri/releases/download/45/log)
- [February 22, 2026: eight flights](https://github.com/TimHanewich/centauri/releases/download/48/log)
- [March 7, 2026: multiple multi-minute flights](https://github.com/TimHanewich/centauri/releases/download/57/log)

Download a `log` file above and pass it to [main.py](./src/main.py) to unpack it, save it as a CSV file, and test your analysis skills!

## Overlaying Telemetry on Video & Dashboarding
Beyond just inspecting the raw numbers, the unpacked telemetry can also be used to overlay live flight data onto video recordings, or fed into any dashboarding/reporting tool (Power BI, Tableau, or even an AI-generated dashboard). I built [Centauri-specific Dashware assets](../../dashware/) that let you overlay telemetry data directly onto a video with only a few clicks and timing syncs.