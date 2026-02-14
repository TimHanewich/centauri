# Failed Flight at Nokomis Community Park on February 13, 2026
This was meant to be the first flight after i built the rear "antenna mast" for the antenna to sit atop. Goal of doing this was keep it away from the battery which I believe was causing Rx issues (see previous flight crash).

What changed between the last flight and this flight:
1. The antenna was positioned ~8 cm higher via the mast
2. I got [a new u.fl to SMA pigtail](https://a.co/d/00RaAXpS) (different quality/make?)
3. This new u.fl to SMA pigtail is longer: 12 inches vs. the old one which was about 6 inches.

Which of the three caused the issue? Likely not #1. Possible #2 (it is just a faulty/cheap quality which lets EMI in), or possibly #3 (doubled exposed area to EMI).

The air was also quite foggy that day. ~83% humidity.

## Files
- Telemetry Log
    - [Raw Log](https://github.com/TimHanewich/centauri/releases/download/45/log)
    - [As .xlsx file with notes](https://github.com/TimHanewich/centauri/releases/download/45/log.xlsx)
- [Onboard video](https://github.com/TimHanewich/centauri/releases/download/45/onboard.AVI)
- [GoPro video](https://youtu.be/4SKdvdp2M-Y)

## Throttle Spike!
As seen in the data below, somehow there was a 99% throttle spike:

![spike](https://i.imgur.com/hgnCwRg.png)

This was NOT a case of the transmitter eroneously sending that to it. I had 20-60% throttle range like I normally do. So what happened here? I believe this was a freak event where the HC-12 on the drone got random data that *happened* to pass the checksum randomly. Hence also the random -32% pitch. 

## Trouble Receiving
As seen in the data above, it was clear the drone had a very hard time getting clean packets. Even only being ~10 feet away from me on the ground, it struggled so much. So much noise. Again, what was the noise caused by (length of new pigtail vs quality of new pigtail), I don't know, but it is really struggling here to get clean data.

## DIAGNOSTIC TESTING
See [here](./tests.md) for some tests I carried out to try to figure out why this happened!

## Misc. Resouces
- [Claude chat about this](https://claude.ai/share/24a049b8-586d-4376-b264-95d6991e2178)