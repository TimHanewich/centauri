# Flying at Nokomis Community Park on February 22, 2026
![img](https://i.imgur.com/Z1927Fs.jpeg)

New this time:
1. Rewired power lines due to burn out in recent high-load testing.
2. Increased checksum from 1-byte (8 bit) to 2-byte (16 bit) to decrease odds of random passing.
3. Drone has Rx Buffer (`ProcessBuffer`) dump logic... if it gets too full of trash, it "dumps it". This avoids it from filling and becoming "clogged" with bad data (not that I have had this problem previously, I don't believe).
4. Ferrite beads and two capacitors added to HC-12 VCC and GND lines to mitigate EMI from ESCs affecting ability of HC-12 to receive.

I only *felt* communication cut out two times. Once, at high altitude. But it descended and recovered. Then, flying over the tree on the right when the orientation had the 5.8 GHz antenna right in between the transmitter and the Rx antenna (or approx in that position). If it had comms issues beyond those two moments, I did not even know as I didn't feel them.

## Conditions
Cloudy day, rain on horizon, even some drops falling from sky at some point, but very few (you can see a drop on the lens at one point).

## Files
- Telemetry
    - [Raw log](https://github.com/TimHanewich/centauri/releases/download/48/log)
    - [Unpacked as CSV](https://github.com/TimHanewich/centauri/releases/download/53/log.csv)
    - [Saved as .xlsx with comments](https://github.com/TimHanewich/centauri/releases/download/53/log.xlsx)
- Onboard video
    - [Raw clip #1](https://github.com/TimHanewich/centauri/releases/download/48/VID00001.AVI)
    - [Raw clip #2](https://github.com/TimHanewich/centauri/releases/download/48/VID00002.AVI)
    - [Raw clip #3](https://github.com/TimHanewich/centauri/releases/download/48/VID00003.AVI)
    - [Raw clip #4](https://github.com/TimHanewich/centauri/releases/download/48/VID00004.AVI)
    - [Raw clip #5](https://github.com/TimHanewich/centauri/releases/download/48/VID00005.AVI)
    - [Raw clip #6](https://github.com/TimHanewich/centauri/releases/download/48/VID00006.AVI)
    - All clips, concatenated: [download](https://github.com/TimHanewich/centauri/releases/download/50/all.avi), [on youtube](https://youtu.be/UTmN95-Z5yM)
- GoPro video (ground-based)
    - [Raw clip #1](https://github.com/TimHanewich/centauri/releases/download/49/GH010345.MP4)
    - [Raw clip #2](https://github.com/TimHanewich/centauri/releases/download/49/GH010346.MP4)
    - [Raw clip #3](https://github.com/TimHanewich/centauri/releases/download/49/GH010347.MP4)
    - [Raw clip #4](https://github.com/TimHanewich/centauri/releases/download/49/GH010348.MP4)
    - [Raw clip #5](https://github.com/TimHanewich/centauri/releases/download/49/GH010349.MP4)
    - [Raw clip #6](https://github.com/TimHanewich/centauri/releases/download/49/GH010350.MP4)
    - [Raw clip #7](https://github.com/TimHanewich/centauri/releases/download/49/GH010351.MP4)
    - [Raw clip #8](https://github.com/TimHanewich/centauri/releases/download/49/GH010352.MP4)
    - [Raw clip #9](https://github.com/TimHanewich/centauri/releases/download/49/GH010353.MP4)
    - [All clips, concatenated on YouTube](https://youtu.be/mt7dAjAIeqw)
- Pictures taken during the day: [On Imgur](https://imgur.com/a/fELYq5p)
        

## Flight Matching
- Flight #1 (11 seconds) = just an onground low-power test before taking off
- Flight #2 (147 seconds)
- Flight #3 (190 seconds) = onboard clip #2, 00:27 to 03:38 of gopro clip #4
    - With Telemetry: [on YouTube](https://youtu.be/VrwWf6sYs7k), [download](https://github.com/TimHanewich/centauri/releases/download/51/export1.mp4)
    - With Telemetry AND angles (angles may be incorrect): [on youtube](https://youtu.be/1ruFgxjx7Bo), [download](https://github.com/TimHanewich/centauri/releases/download/51/export2_angles.mp4)
- Flight #4 (3 seconds)
- Flight #5 (171 seconds)
- Flight #6 (59 seconds) - *realized there was low battery on FPV monitor and flew back to plug it in*
- Flight #7 (158 seconds) = onboard clip #5, 02:13 to 04:51 of gopro clip #6
    - With Telemetry: [on youtube](https://youtu.be/M7sAEZuMz2I), [download](https://github.com/TimHanewich/centauri/releases/download/52/export2_noangles.mp4)
    - With Telemetry AND angles (angles may be incorrect): [on youtube](https://youtu.be/oPxl2cfeXX0), [download](https://github.com/TimHanewich/centauri/releases/download/52/export1.mp4)
- Flight #8 (246 seconds) - *fly bys of camera*

## Batteries
Both batteries were used and flown down to approx. 15.1 volts.
- Battery #1 absorbed 1,936 mAh charging afterwards.
- Battery #2 absorbed 1,893 mAh charging afterwards.

Altogether, that is **3,829 mAh** consumed, or **56.67 Wh** (nominal voltage of 14.8v for 4S LiPo).

Flight time was approximately **971 seconds** (16.2 minutes). That comes out to an average power draw of **210 watts**!

This is a rate of 236 mAh/minute, which would give me a theoretical max flight time of ~13.9 minutes on these 3,300 mAh 4S LiPo batteries.

## Extending Range from Here
- Transmitter side:
    - Maybe the CP2102 is not supplying the Pi with enough current?
    - Maybe the Pi is not supplying the HC-12 with enough current?
    - Is the power supply the HC-12 is getting clean?
    - No ground plane? Put cookie sheet beneath antenna?