# Test Flying at Nokomis Community Park on Jan 24, 2026
This was supposed to be the first flight with **new 433 MHz external antenna** and **brand new AIO FPV module** with the **new protective FPV AIO module holder I made**.

Range was horrible. Possibly worse than it used to be when I first started with the spring antenna?

I originally did a props off test where i walked to the far end of the field with it armed, running at 8% throttle (no PID values). I did this when I began and saw it was still running at the far side of the field which gave me hope. It would only cut out for a moment and then come back on.

After that simple range test, I did the same thing, this time with the FPV AIO module plugged in (transmitting at 5.8 GHZ), maybe it was cutting out a BIT more, but it wasn't enough to panic me. I think it was acceptable.

Then I put props on and flew, slow paced range test. Lost control much much earlier. How is that possible? Thinking about it, I think my first range test was falsely informing me that it could go to far end of range. What I think actually happened: I was using the motors turning off as an indication I have lost signal. Really, all that meant was a single command packet hadn't been received for > 2s (I have a 2s fail safe on it). SO, update rate at that point was probably already bad! And that is what was happening when I crashed... not once did the drone ever just cut out mid-air... instead, the update rate would drop so low (it wasn't receiving command control packets quickly enough) that my command feed would stop arriving at it and it would tilt over and crash!

So going back to the range test where I walked it... there was no way for me to see that! No way for me to see *some* dropped packets. Instead, I *thought* it was all fine just up until the motors turned off. In reality, the packet refresh rate was probably so low, but still faster than once every 2 seconds, which is why the motors stopped.

Possibly seems like HC-12 performance degrading? Used to be better even with spring antenna? Is that possible? Maybe the transmiter side.

## The Good
- The FPV AIO module did well. Good solid signal.
- The new frame I have for the FPV AIO module did protect it on a few rolls. The antenna was bent, but not broken off.
- Motors weren't turning off when behind tree. So at least 1 packet every 2s was being received.

## The Bad
- Range of HC-12 w/ 433 MHz antennas is really bad. Possible worse, or as bad as before? Or maybe a bit better?

## Possible Causes
- The [433 MHz antennas I am using](https://a.co/d/19jyKZY) are low quality, not resonating at 433 MHz.
- The HC-12's I am using are "burnt out" (ability to transmit/receive degraded). Possible more risk of the one attached to the PC as that has done most of the transmitting the most... maybe it is transmitting at lesser power.
- I am flying too close to the ground? That could be an issue. Since I am creeping closely to the ground to minimize drop distance, that could be an issue. (notice the crashes come when I am only a foot or so off the ground!)

If I had to guess on the true cause, I would guess it is a combination of all three... these 433 MHz antennas are probably cheap and poorly tuned *and* I was flying so close to the ground? How do I reckon it was not JUST the ground? Because when I crashed, the 5.8 GHz feed was still good! The ground would have killed that too if that was the problem I believe. But if I flew higher at that point, probably wouldnt have crash. **So I think poor 433 MHz antennas are severely hampering the HC-12's connection**.

[This Google Gemini thought](https://gemini.google.com/share/10aa1f02d1a2) is interesting as well.

## Next Steps:
- **For debugging purposes**: Add "last received (ms)" property into telemetry to track how recently a valid control packet was received. This will important to look back at to see how much were dropping when.
- **For debugging purposes**: MAYBE build in like "range test" mode on drone... where the onboard LED instead blinks based on good command receive rate (i.e. > 15 Hz), so it is easier to tell when it cuts out
- **To fix this**: Buy better quality 433 MHz radio antennas. Perhaps these ones aren't resonant at 433 MHz
    - https://a.co/d/g7YIyoq
    - https://a.co/d/4ahDuLe
    - https://a.co/d/97MMvc5
- **To fix this**: Investigate dropping over-the-air baudrate on HC-12s to minimum needed to support 20 Hz command control refresh rate
    - This won't be possible. See [this research](https://x.com/TimHanewich/status/2015243980959588374)
- **To fix this**: ensure the HC-12 being used by the PC transmitter (attache to transceiver platform) is still on correct channel, full power, FU3 mode, AND the transmission power isn't reduced due to wear and tear on it (compare to another?)

## Videos
- [GoPro](https://youtu.be/ar4hZ_MQKu0) (raw concatenated)
- Onboard (raw concatenated)
    - [On YouTube](https://youtu.be/pzK3nCJYQHY)
    - [Raw download](https://github.com/TimHanewich/centauri/releases/download/27/all.avi)

## Files
- [Raw telemetry log](https://github.com/TimHanewich/centauri/releases/download/28/log) (contains other flights from previous too)
- [Unpacked telemetry log, as CSV](https://github.com/TimHanewich/centauri/releases/download/29/log.csv)
- [Telemetry log, as .xlsx, with some play-by-play commentary of crash](https://github.com/TimHanewich/centauri/releases/download/29/log.xlsx)

## Fresnel Zone Calculations

### At Point of Crash at 2:48 in Telemetry
![crash location](https://i.imgur.com/iKJkKpb.png)

Crash was probably about 31 meters out.

Radius of the fresnel zone at center is ~7.6 ft at this distance

![fresnel calc](https://i.imgur.com/H4xMi9o.png)

Recommendation I have seen calculated by AI is the receiver needs to be at least **1.4 meters** (**4.6 ft**) off the ground at this distnace

### At Max Distance in Field (walking test I did)
![distance](https://i.imgur.com/TwDHx3g.png)

About 100 meters out.

Radius of fresnel zone at center is ~13.6 ft at this distance.

![freshnel calc](https://i.imgur.com/XuDZiL5.png)

[Recommendation from AI based on calculations](https://gemini.google.com/share/849f778bb79a) is, at 100 meters away and on the 433 MHz band, receiver + transmitter need to be **2.5 meters** (**8.2 feet**) above the ground at least! During my walking test (see [this video at 2:54](https://youtu.be/ar4hZ_MQKu0?t=174)) I was holding it chest height, so maybe ~4 ft. Which explains why it was cutting in and out.
