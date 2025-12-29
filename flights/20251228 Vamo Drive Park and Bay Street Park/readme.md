# Flying at Vamo Drive park and Bay Street Park on December 28, 2025
I flew in both [Vamo Drive Park](https://maps.app.goo.gl/5sxLHPCa2zMVefum8) and [Bay Street Park](https://maps.app.goo.gl/BQ8zuRWscRzio19r9) on December 28, 2025.

![flights](https://i.imgur.com/DqE4Vl8.png)

## Footage
- [All video from ground (on GoPro), raw, concatenated](https://youtu.be/PpSTQVRufBo)
- [All video from onboard, concatenated raw](https://youtu.be/ZRmKvO1-QWs) - *recorded in variable frame rate by the FPV monitor, so beware of timing issues*
- [All video from onboard, concatenated,  re-encoded as 30 fps constant frame rate](https://youtu.be/ZYWoqG6bNVE)
- [Flight 6 with Telemetry overlay](https://youtu.be/cTK0w3Zb9RU)

## Files
- [Raw telemetry log](https://github.com/TimHanewich/centauri/releases/download/19/log)
- [Telemetry log, unpacked as .csv file](https://github.com/TimHanewich/centauri/releases/download/19/log.csv)
- [Telemetry log as .xlsx, with notes on flights](https://github.com/TimHanewich/centauri/releases/download/19/log.xlsx)
- [Pictures from the day](https://imgur.com/a/rz63IIc)
    - [At Vamo Drive Park](https://i.imgur.com/mTkFzfr.jpeg)
    - [At Bay Street Park](https://i.imgur.com/tjubIXg.jpeg)

## Batteries
- Battery 1 was flown down to 14.8v (resting) and absored 2,935 mAh to fully charge afterwards
- Battery 2 was flown down to 15.1v (resting) and absored 2,401 mAh to fully charge afterwards

## Avg. Current Draw
Using the data collected, we can calculate the average current draw Centauri consumes in flight. Battery #1 was flown for 787 seconds, or 13 minutes and 7 seconds. Battery #1 was re-charged 2,935 mAh later that day, so it is safe to say it was depleted 2,935 mAh from that 13:07 of flight time. So, dividing the mAh consumed by the seconds of flight time, we find Centauri consumes ~3.73 mAh per second. This is ~223.8 mAh per minute, or ~13,426 mAh per hour. Dividing that by 1,000 to go from mAh to Ah, that would be ~13.4 Ah per hour, or an average consumption of **13.4 amps**.

The second battery consumed 2,401 mAh across 645 seconds of flight time. Applying the same math as above, this is also **13.4 amps** on average!

Note: this calculation assumes current consumption is very low while powered on but unarmed, as there was a bit of that too. And, this was *with* the FPV camera plugged in drawing energy, which is not really a *necessary* component.