# Flying at Nokomis Community Park on Feb 10, 2026
This was also the first time flying after the level1 and level2 replacements (rebuild) in the very heavy crash several days ago.

First time flying with new rear left arm for the antenna mounting, not the rear right in the mid-section.

![new antenna position](https://i.imgur.com/1P4goUB.jpeg)

## Antennas Used
- Tx Antenna used by transmitter = [FLEXI-SMA-433](https://www.digikey.com/en/products/detail/rf-solutions/FLEXI-SMA-433/2781767), ~1.5 SWR in my NanoVNA tests.
- Rx Antenna on Drone = [TI.10.0111](https://www.digikey.com/en/products/detail/taoglas-limited/TI-10-0111/3131969), ~1.1 SWR in my NanoVNA tests.

## Files
- Telemetry
    - [Raw](https://github.com/TimHanewich/centauri/releases/download/37/log) (contains testing at home as well, only pay attention to last armed flight)
    - [As .xlsx with notes](https://github.com/TimHanewich/centauri/releases/download/39/log.xlsx)
- Onboard Footage
    - [Raw Clip #1](https://github.com/TimHanewich/centauri/releases/download/37/VID00001.AVI) (flight 1)
    - [Raw Clip #2](https://github.com/TimHanewich/centauri/releases/download/37/VID00002.AVI) (flight 2)
    - Flight #1 with telemetry overlay: [on youtube](https://youtu.be/nFCayAlaNMg), [direct download](https://github.com/TimHanewich/centauri/releases/download/38/export1.mp4)
    - Flight #1 with telemetry overlay, *including angles (may be incorrect angles?)*: [on youtube](https://youtu.be/g6PuntiMJ7I), [direct download](https://github.com/TimHanewich/centauri/releases/download/41/WITH_ANGLES.mp4)
- GoPro Footage (Ground based): 
    - [on youtube, concatenated](https://youtu.be/zpdaJTlGbDk) (4K quality)
    - [Raw clip #1 direct download](https://github.com/TimHanewich/centauri/releases/download/42/1.MP4)
    - [Clip #2, part 1 direct download](https://github.com/TimHanewich/centauri/releases/download/42/2_part1.mp4) (split into 2 chunks to make it < 2GB so could upload to GitHub)
    - [Clip #2, part 2 direct download](https://github.com/TimHanewich/centauri/releases/download/42/2_part2.mp4) (split into 2 chunks to make it < 2GB so could upload to GitHub)
- [Pictures](https://imgur.com/a/Okmq0Vv)
- Other media
    - Two-Perspective Compilation of the crash, with timings: [on youtube](https://youtu.be/mjyGw9TXAto), [direct download](https://github.com/TimHanewich/centauri/releases/download/40/export6.mp4)

## Telemetry Not Recorded
Unfortunately flight #2 telemetry did not save. Note as to why is saved in the log.

![why](https://i.imgur.com/69wxvXq.png)

## Crash
Crashed approx. 83 meters away.

![crash](https://i.imgur.com/pB8ESwp.png)

If you see the recording, you will see the motors shut off mid-air. 2s had elapsed since a packet was received, so failsafe activated.

The front right arm broke after flipping:

![cracked arm](https://i.imgur.com/5nXyn3G.jpeg)

At the moment the command telemetry feed was cut off (radio signals not arriving):
- Estimated drone (Rx) height = **5.5 feet**
- Transmitter (Tx) height = **2.5 feet** (resting on picnic table)
- Distance to transmitter = **approx. 83 meters**
- Orientation of drone probably positioned closely where the 4S LiPo battery may have been blocking (or slightly blocking?) direct line of sight between Tx antenna and Rx antenna
- A chainlink fence was directly beind the drone (not in between drone and transmitter to be clear), maybe 6-8 feet behind.